from machine import Pin, ADC
from bp5pins import *

class Analog:
  __doc__ = \
  '''Manages the analog-to-digital conversion using ADC and shift register.
  adc = Analog(SR, DISP)
    where:
      SR           shift register class
      DISP         TFT display class
  Class functions:
    select( ch )   configures the MUX to the specified channel
    deselect()     disables the MUX
    read( ch )     read the ADC after switching the MUX channel
    read()         read the ADC uses currently selected MUX channel
    isense()       reads current sense, returns mA (doesn't use MUX)
    strings()      all channel voltages as list of strings
    all()          all channel voltages as numerical values
    print()        prints all channels voltages, args:
      clear        clears screen, default=True
      display      prints to the display, default=True
      console      prints to the console, default=True
  Constants:
    Analog MUX channels:
      BPIO0 ... BPIO7   I/O connector signals
      VUSB              incoming USB voltage
      CURRENT_DETECT    current sense 
      VREG_OUT          power supply voltage
      MUX_VREF_OUT      I/O connector Vout'''

  def help(self):
    print(self.__doc__)

  # Note: assign analog input "channel" numbers here 
  # in this class so that the IO pins are in numerical order,
  # unlike how they are physically wired to the mux.
  # The remaining four channels are left alone.

  # MUX CHANNELS:
  # -------------
  BPIO0           =  7 #  "BPIO0"
  BPIO1           =  6 #  "BPIO1"
  BPIO2           =  5 #  "BPIO2"
  BPIO3           =  4 #  "BPIO3"
  BPIO4           =  3 #  "BPIO4"
  BPIO5           =  2 #  "BPIO5"
  BPIO6           =  1 #  "BPIO6"
  BPIO7           =  0 #  "BPIO7"
  VUSB            =  8 #  " VUSB"
  CURRENT_DETECT  =  9 #  " IDET"
  VREG_OUT        = 10 #  " VREG"
  MUX_VREF_OUT    = 11 #  "MUXVR"

  LBL_BPIO0           = " IO0"
  LBL_BPIO1           = " IO1"
  LBL_BPIO2           = " IO2"
  LBL_BPIO3           = " IO3"
  LBL_BPIO4           = " IO4"
  LBL_BPIO5           = " IO5"
  LBL_BPIO6           = " IO6"
  LBL_BPIO7           = " IO7"
  LBL_VUSB            = "VUSB"
  LBL_CURRENT_DETECT  = "IDET"
  LBL_VREG_OUT        = "VREG"
  LBL_MUX_VREF_OUT    = "MUXV"

  UNITS_BPIO0           = "V"
  UNITS_BPIO1           = "V"
  UNITS_BPIO1           = "V"
  UNITS_BPIO2           = "V"
  UNITS_BPIO3           = "V"
  UNITS_BPIO4           = "V"
  UNITS_BPIO5           = "V"
  UNITS_BPIO6           = "V"
  UNITS_BPIO7           = "V"
  UNITS_VUSB            = "V"
  UNITS_CURRENT_DETECT  = "mA"
  UNITS_VREG_OUT        = "V"
  UNITS_MUX_VREF_OUT    = "V"

  NCHAN = 12
  AIN = (
    BPIO0, BPIO1, BPIO2, BPIO3,
    BPIO4, BPIO5, BPIO6, BPIO7,
    VUSB, CURRENT_DETECT,
    VREG_OUT, MUX_VREF_OUT,
  )
  # short labels for printing
  LABELS = (
    LBL_BPIO0, LBL_BPIO1, LBL_BPIO2, LBL_BPIO3,
    LBL_BPIO4, LBL_BPIO5, LBL_BPIO6, LBL_BPIO7,
    LBL_VUSB, LBL_CURRENT_DETECT,
    LBL_VREG_OUT, LBL_MUX_VREF_OUT,
  )
  UNITS = (
    UNITS_BPIO0, UNITS_BPIO1, UNITS_BPIO2, UNITS_BPIO3,
    UNITS_BPIO4, UNITS_BPIO5, UNITS_BPIO6, UNITS_BPIO7,
    UNITS_VUSB, UNITS_CURRENT_DETECT,
    UNITS_VREG_OUT, UNITS_MUX_VREF_OUT,
  )
  # analog voltages are divided by two
  # before being read by the ADC
  PRESCALE_FACTOR = 2.0
  ADC_MAX_VOLTS = 3.3
  # note: the ADC is 12 bits, but
  # micropython scales the reading to 16 bits
  ADC_MAX_COUNTS = 64 * 1024
  # multiply the raw reading by scale factor to get voltage
  VSCALE_FACTOR = PRESCALE_FACTOR * ( ADC_MAX_VOLTS / ADC_MAX_COUNTS )
  #
  # scale factor, current sense, 
  # 0-3.3 V = 0 to 500 mA
  ISENSE_MAX_MILLIAMPS = 500.0
  ISCALE_FACTOR = ISENSE_MAX_MILLIAMPS * ( ADC_MAX_VOLTS / ADC_MAX_COUNTS )

  # Related Shift Register bits:
  # MASK_AMUX_EN              = 1<<0
  # MASK_AMUX_S0              = 1<<1
  # MASK_AMUX_S1              = 1<<2
  # MASK_AMUX_S2              = 1<<3
  # MASK_AMUX_S3              = 1<<4

  def getbit( self, value, bitnum ):
    return int((value & (1<<bitnum)) > 0)

  def __init__(self, sr, disp):
    self.sr = sr
    self.disp = disp
    self.amux = ADC(Pin(PIN_ANALOG_MUX))
    self.isense = ADC(Pin(PIN_CURRENT_SENSE))

  def deselect( self ):
    self.sr.set_bits(self.sr.MASK_AMUX_EN)
    self.sr.send()

  def select( self, channel ):
    self.sr.clr_bits(self.sr.MASK_AMUX_S0)
    self.sr.clr_bits(self.sr.MASK_AMUX_S1)
    self.sr.clr_bits(self.sr.MASK_AMUX_S2)
    self.sr.clr_bits(self.sr.MASK_AMUX_S3)
    if self.getbit( channel, 0 ): self.sr.set_bits(self.sr.MASK_AMUX_S0)
    if self.getbit( channel, 1 ): self.sr.set_bits(self.sr.MASK_AMUX_S1)
    if self.getbit( channel, 2 ): self.sr.set_bits(self.sr.MASK_AMUX_S2)
    if self.getbit( channel, 3 ): self.sr.set_bits(self.sr.MASK_AMUX_S3)
    # mux enable, active low
    self.sr.clr_bits(self.sr.MASK_AMUX_EN)
    self.sr.send()

  def read( self, channel=None ):
    if channel is None:
      val = self.amux.read_u16() * self.VSCALE_FACTOR
    else:
      self.select(channel)
      val = self.read()
      self.deselect()
    return val

  def strings_disp(self):
    out = []
    for ich in range(self.NCHAN):
      out.append(
        f'{self.LABELS[ich]}: '
        f'{self.read(self.AIN[ich]):5.3f} '
        f'{self.UNITS[ich]}')
    return out

  def strings(self):
    return self.strings_disp()

  def __repr__(self):
    return '\n'.join( self.strings() )

  def __str__(self):
    return '\n'.join( self.strings() )

  def all(self):
    values = []
    for ich in range(self.NCHAN):
      values.append( self.read( self.AIN[ich] ))
    return values

  def isense( self ):
    return self.isense.read_u16() * self.ISCALE_FACTOR

  def print(self, clear=True, display=True, console=True):
    """Show the ADC voltages on the screen"""
    if clear: self.disp.cls()
    results = self.strings() # reads all voltages
    # print the I/O pins first
    for row, result in enumerate(results[0:8]):
      if console: print(result)
      if display: self.disp.text( result, row, 0 )
    # print other voltages next
    if display:
      v = results[10] # VREG
      self.disp.text( v, 8, 0 )
      i = results[9] # IDET
      self.disp.text( i, 9, 0 )
    if console:
      for row, result in enumerate(results[8:]):
        print(result)


