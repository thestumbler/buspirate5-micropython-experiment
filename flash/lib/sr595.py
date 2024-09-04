from machine import SPI, Pin
import time
from bp5pins import *

class SR:

  # Simple 595 Shift Regsiter class
  # used to control the expander I/O bits
  # ----
  # U501/QA#15   0   AMUX_EN
  # U501/QB#1    1   AMUX_S0
  # U501/QC#2    2   AMUX_S1
  # U501/QD#3    3   AMUX_S2
  # U501/QE#4    4   AMUX_S3
  # U501/QF#5    5   DISPLAY_BACKLIGHT
  # U501/QG#6    6   DISPLAY_RESET
  # U501/QH#7    7   PULLUP_EN
  # ----
  # U502/QA#15   0   N/C
  # U502/QB#1    1   CURRENT_EN
  # U502/QC#2    2   N/C
  # U502/QD#3    3   CURRENT_RESET
  # U502/QE#4    4   DAC_CS
  # U502/QF#5    5   CURRENT_EN_OVERRIDE
  # U502/QG#6    6   N/C
  # U502/QH#7    7   N/C
  # ----
  # I/O expander bit mask definitions:

  AMUX_EN              = 0
  AMUX_S0              = 1
  AMUX_S1              = 2
  AMUX_S2              = 3
  AMUX_S3              = 4
  DISPLAY_BACKLIGHT    = 5
  DISPLAY_RESET        = 6
  PULLUP_EN            = 7
  #UNUSED              = 8
  CURRENT_EN           = 9
  #UNUSED              = 10
  CURRENT_RESET        = 11
  DAC_CS               = 12
  CURRENT_EN_OVERRIDE  = 13
  #UNUSED              = 14
  #UNUSED              = 15

  MASK_AMUX_EN              = 1 << AMUX_EN             
  MASK_AMUX_S0              = 1 << AMUX_S0             
  MASK_AMUX_S1              = 1 << AMUX_S1             
  MASK_AMUX_S2              = 1 << AMUX_S2             
  MASK_AMUX_S3              = 1 << AMUX_S3             
  MASK_DISPLAY_BACKLIGHT    = 1 << DISPLAY_BACKLIGHT   
  MASK_DISPLAY_RESET        = 1 << DISPLAY_RESET       
  MASK_PULLUP_EN            = 1 << PULLUP_EN           
  #MASK_UNUSED              = 1 << UNUSED8
  MASK_CURRENT_EN           = 1 << CURRENT_EN
  #MASK_UNUSED              = 1 << UNUSED10
  MASK_CURRENT_RESET        = 1 << CURRENT_RESET       
  MASK_DAC_CS               = 1 << DAC_CS
  MASK_CURRENT_EN_OVERRIDE  = 1 << CURRENT_EN_OVERRIDE
  #MASK_UNUSED              = 1 << UNUSED14
  #MASK_UNUSED              = 1 << UNUSED15
  # ----

  bit_defns = [
      (  0, 'AMUX_EN' ),
      (  1, 'AMUX_S0' ),
      (  2, 'AMUX_S1' ),
      (  3, 'AMUX_S2' ),
      (  4, 'AMUX_S3' ),
      (  5, 'DISPLAY_BACKLIGHT' ),
      (  6, 'DISPLAY_RESET' ),
      (  7, 'PULLUP_EN' ),
      (  9, 'CURRENT_EN' ),
      ( 11, 'CURRENT_RESET' ),
      ( 12, 'DAC_CS' ),
      ( 13, 'CURRENT_EN_OVERRIDE' ),
    ]

  # maintain shadow buffer of SR output pins
  # outputs should always follow the SR pins
  outputs = int.from_bytes( bytearray( b'\x00\x00'), 'big' )
  # temporary buffer used to construct an new output value
  pending = outputs

  def __init__(self, _spi):
    self.spi = _spi
    self.oena = Pin(PIN_SHIFT_EN, Pin.OUT, value=1)
    self.xfer = Pin(PIN_SHIFT_LATCH, Pin.OUT, value=0)

    self.enable() # no RGB LED before this
    self.init()

  # initialized state: 
  # * bits to be cleared:
  #   CURRENT_EN_OVERRIDE, 
  # * bits to be setshift :
  #   AMUX_S3
  #   AMUX_S1
  #   DISPLAY_RESET
  #   CURRENT_EN
  def init(self):
    self.output = int.from_bytes( bytearray( b'\x00\x00'), 'big' )
    self.clr_bits( self.MASK_CURRENT_EN_OVERRIDE )
    self.set_bits( self.MASK_AMUX_S3 )
    self.set_bits( self.MASK_AMUX_S1 )
    self.set_bits( self.MASK_DISPLAY_RESET )
    self.set_bits( self.MASK_CURRENT_EN )
    self.send()

  def __repr__(self):
    #print( 'oena:', self.oena.value(), 'xfer:', self.xfer.value() )
    print(f'Shadow register: 0x{self.output:04x}')
    for bit in self.bit_defns:
      ibit = bit[0]
      name = bit[1]
      mask = 1 << ibit
      val = (self.outputs & mask) >> ibit
      print(f'bit {ibit:3d}:   {val}   {name}')

  def __str__(self):
    self.__repr__()

  def get_bit( self, ibit ):
    if self.outputs != self.pending: return None
    return (self.outputs & (1 << ibit)) >> ibit
  def set_bit( self, ibit ):
    self.pending = self.pending | (1 << ibit )
  def clr_bit( self, ibit ):
    self.pending = self.pending & ~(1 << ibit )

  def set_bits( self, masks ):
    self.pending = self.pending | masks
  def clr_bits( self, masks ):
    self.pending = self.pending & ~masks

  # functions to do weird bit craziness
  # Bit reverse an 8 bit value
  def rbit8(self,v):
      v = (v & 0x0f) << 4 | (v & 0xf0) >> 4
      v = (v & 0x33) << 2 | (v & 0xcc) >> 2
      return (v & 0x55) << 1 | (v & 0xaa) >> 1
  # inverts and reverses bits
  def invert(self, buff):
    ibuff = bytearray()
    for v in buff:
      ibuff.append( 0xff ^ v )
    return ibuff
  def backwards(self, buff):
    ibuff = bytearray()
    for v in buff:
      ibuff.append( self.rbit8(v) )
    return ibuff
  
  def send(self):
    self.spi.write(bytearray(self.pending.to_bytes(2,'big')))
    self.outputs = self.pending
    self.transfer()

  def send_raw(self, val16):
    val = val16 % 0xffff
    self.send_buff(bytearray(val.to_bytes(2,'big')))
    self.outputs = val
    self.pending = val

  def enable(self):
    self.oena.value(0)
    return self.oena.value()

  def disable(self):
    self.oena.value(1)
    return self.oena.value()

  def transfer(self):
    self.xfer.value(1)
    time.sleep_us(10)
    self.xfer.value(0)
    time.sleep_us(10)

