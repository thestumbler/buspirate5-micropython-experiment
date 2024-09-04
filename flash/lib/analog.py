from machine import Pin, ADC
from bp5pins import *

class Analog:

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

  def __init__(self, sr):
    self.sr = sr
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

  def strings(self):
    out = []
    for ich in range(self.NCHAN):
      out.append( f'{self.LABELS[ich]}: {self.read(self.AIN[ich]):6.3}')
    return out

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

