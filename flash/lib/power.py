from machine import Pin, PWM
import time
from bp5pins import *


# AP2127 regulator
# Vout = Vreg * ( 1 + R1 / R2 )
# Vreg = 0.8 V
# without any PWM from MCU:
# R1 = 133 Kohm
# R2 = 33 Kohm
# R0 = 102 Kohm

#
# PWM input signal (static):
# 0 V    5.067 V
# 1      3.763
# 2      2.460
# 3      1.156
# 3.3    0.764
#
#  0 to 3.3 V ==> 5.067 to 0.764 V
#  Vpwm span = 3.3 V
#  Vout span = 4.303 V
# 
# Vout = 5.0 - Vpwm * (4.3/3.3)
# Vpwm = ( 5.0 - Vout ) * (3.3/4.3)
#

# shift register outputs of interest
#  MASK_CURRENT_EN           = 1<<9   active low
#  MASK_CURRENT_RESET        = 1<<11  active high
#  MASK_CURRENT_EN_OVERRIDE  = 1<<13  active high

class Power:
  '''Adjustable Power Supply management class.
  psu = Power(SR, ADC)
    where:
      SR           shift register class
      ADC          analog to digital converter class
  Class functions:
    enable()             enable VREG output
    disable()            disable VREG output
    reset()              resets current limiter
    enable_override()    enable current limiter override
    disable_override()   disable current limiter override
    voltage()            get voltage, V
    voltage(voltage)     set voltage, V
    current()            get current, mA
    current(current)     set current, mA
    measure()            measure voltage (V) and current (mA)
    setpoint()           show voltage (V) and current (mA) setpoint
    control()            show control bits ENABLE and OVERRIDE
    ramp()               ramps power supply for calibration testing
  '''

  def help(self):
    print(self.__doc__)

  # duty factor in counts covered 16 bit range
  MAX_DUTY_COUNTS = 64 * 1024

  # scale factor, current limit (same as current sense) 
  # 0-3.3 V = 0 to 500 mA
  MAX_IADJ_MA = 500.0
  # multiply current limit value in mA by this scale factor
  # to get duty factor in PWM counts
  ISCALE_FACTOR = MAX_DUTY_COUNTS / MAX_IADJ_MA 

  # Vout = 5.0 - Vpwm * (3.8/3.3)
  MAX_VOUT = 5.067
  MIN_VOUT = 0.764
  MAX_VPWM = 3.3 # MIN VPWM is 0
  VOUT_DELTA = MAX_VOUT - MIN_VOUT # 3.8 V
  VPWM_DELTA = 3.3
  VSCALE_FACTOR_VOLTS = VOUT_DELTA / VPWM_DELTA
  VSCALE_FACTOR_COUNTS = MAX_DUTY_COUNTS / MAX_VPWM

  def vpwm2vout( self, vpwm ):
    vout = self.MAX_VOUT - (vpwm * self.VSCALE_FACTOR_VOLTS)
    return vout
  def vout2vpwm( self, vout ):
    vpwm = (self.MAX_VOUT - vout) / self.VSCALE_FACTOR_VOLTS
    return vpwm

  DEF_VOLTAGE = 5.0
  DEF_CURRENT = 250

  def __init__(self, sr, adc):
    self.pwm_vreg = PWM( Pin(PIN_VREG_ADJUST),    freq=10000, duty_u16=0)
    self.pwm_iadj = PWM( Pin(PIN_CURRENT_ADJUST), freq=10000, duty_u16=0)
    self.sr = sr
    self.adc = adc
    self.sr.set_bits(self.sr.MASK_CURRENT_EN)
    self.sr.clr_bits(self.sr.MASK_CURRENT_RESET)
    self.sr.clr_bits(self.sr.MASK_CURRENT_EN_OVERRIDE)
    self.sr.send()
    self.voltage(self.DEF_VOLTAGE)
    self.current(self.DEF_CURRENT)
    self.enable()


  def enable( self ):
    self.sr.clr_bits(self.sr.MASK_CURRENT_EN)
    self.sr.send()

  def disable( self ):
    self.sr.set_bits(self.sr.MASK_CURRENT_EN)
    self.sr.send()

  def reset( self ):
    self.sr.set_bits(self.sr.MASK_CURRENT_RESET)
    self.sr.send()
    time.sleep_ms(10)
    self.sr.clr_bits(self.sr.MASK_CURRENT_RESET)
    self.sr.send()

  def enable_override( self ):
    self.sr.set_bits(self.sr.MASK_CURRENT_EN_OVERRIDE)
    self.sr.send()

  def disable_override( self ):
    self.sr.clr_bits(self.sr.MASK_CURRENT_EN_OVERRIDE)
    self.sr.send()


  def voltage( self, voltage=None ):
    if voltage is not None:
      if voltage > self.MAX_VOUT: voltage = self.MAX_VOUT
      if voltage < 0: voltage = 0
      vpwm = self.vout2vpwm(voltage) 
      df16 = int( self.VSCALE_FACTOR_COUNTS * vpwm )
      if df16 > self.MAX_DUTY_COUNTS: df16 = self.MAX_DUTY_COUNTS
      if df16 < 0: df16 = 0
      self.pwm_vreg.duty_u16(df16)
    # return voltage setpoint
    df16 = self.pwm_vreg.duty_u16()
    vpwm = df16 / self.VSCALE_FACTOR_COUNTS
    vout = self.vpwm2vout( vpwm )
    return vout

  def current( self, current=None ):
    if current is not None:
      if current > self.MAX_IADJ_MA: current = self.MAX_IADJ_MA
      if current < 0: current = 0
      df16 = int( current * self.ISCALE_FACTOR )
      if df16 > self.MAX_DUTY_COUNTS: df16 = self.MAX_DUTY_COUNTS
      if df16 < 0: df16 = 0
      self.pwm_iadj.duty_u16(df16)
    # return current setpoint
    df16 = self.pwm_iadj.duty_u16()
    iadj = df16 / self.ISCALE_FACTOR
    return iadj

  def measure(self):
    meas_voltage = self.adc.read( self.adc.VREG_OUT )
    meas_current = self.adc.read( self.adc.CURRENT_DETECT )
    return f'Meas:  {meas_voltage:6.3f} V  {meas_current:>8.3f} mA'

  def setpoint(self):
    return f'SetP:  {self.voltage():6.3f} V  {self.current():>8.3f} mA'

  def control(self):
    enable = self.sr.get_bit( self.sr.CURRENT_EN )
    override = self.sr.get_bit( self.sr.CURRENT_EN_OVERRIDE )
    fenable = 'Y' if enable == 0 else 'N'
    foverride = 'Y' if override == 1 else 'N'
    return f'Ctrl:  Enable {fenable}  Override {foverride}'

  def __repr__(self):
    out = []
    out.append( self.setpoint() )
    out.append( self.measure() )
    out.append( self.control() )
    return '\n'.join( out )

  def __str__(self):
    return self.__repr__()

  def ramp(self):
    # ramp Vpwm from 0 to 3.3 steps of 0.1 V
    vsave = self.voltage()
    isave = self.current()
    for i in range(33):
      # calculate Vpwm and corresponding Vout
      vpwm = float(i)/10.0
      vout = self.vpwm2vout(vpwm)
      # set the PWM voltage
      df16 = int( self.VSCALE_FACTOR_COUNTS * vpwm )
      if df16 > self.MAX_DUTY_COUNTS: df16 = self.MAX_DUTY_COUNTS
      if df16 < 0: df16 = 0
      self.pwm_vreg.duty_u16(df16)
      time.sleep_ms(250)
      # read the actual voltage
      vadc = self.adc.read(self.adc.VREG_OUT)
      print(f'Vpwm {vpwm:>5.2f}  Vout {vout:>5.2f}  Vadc {vadc:>5.2f}')
    # reset the previous voltage / current
    self.voltage(vsave)
    self.current(isave)

  def testme(self):
    vplist = [ 0, 1, 2, 3, 3.3, ]
    for vp in vplist:
      print(f'Vpwm {vp:>5.2f} => Vout {self.vpwm2vout(vp):>5.2f}')
    print()
    volist = [ 5, 3.85, 2.70, 1.55, 1.20 ]
    for vo in volist:
      print(f'Vout {vo:>5.2f} => Vpwm {self.vout2vpwm(vo):>5.2f}')








