from machine import Pin, UART, SPI

class BP5BIT:

  def dir_string( self, d ):
    if   d == Pin.IN:         return '0=INPUT     '
    elif d == Pin.OUT:        return '1=OUTPUT    '
    elif d == Pin.OPEN_DRAIN: return '2=OPEN_DRAIN'
    return                          f'{d}=UNKNOWN   '

  def __init__(self, iobit, pin_num_io, pin_num_dir, direction):
    self.iobit = iobit
    self.pin_num_dir = pin_num_dir
    self.pin_num_io = pin_num_io
    self.dir = Pin( self.pin_num_dir, Pin.OUT ) 
    self.mode(direction)

  def mode(self, direction):
    self.direction = direction
    self.pin = Pin( self.pin_num_io, direction )
    if self.direction == Pin.OUT:
      self.dir.on()
    else:
      self.dir.off()

  def __repr__(self):
    return \
    f'IO.{self.iobit}: ' \
    f'GPIO{self.pin_num_io:02d} V:{self.pin.value()} ' \
    f'D:{self.dir_string(self.direction)}        ' \
    f'DIR{self.pin_num_dir} V:{self.dir.value()}'

  def value( self, val=None ):
    if val is None:
      return self.pin.value()
    else:
      return self.pin.value(val)
  def on( self ):
    return self.pin.on()
  def off( self ):
    return self.pin.off()

class BP5IO:
  pinout_strings= [
    'IO0  SDA     ',
    'IO1  SCL     ',
    'IO2          ',
    'IO3          ',
   #'IO4  TX  SCLK', # BP5 original pinouts for SPI
   #'IO5  RX  MOSI', # can't use with default RP2040
   #'IO6      MISO',
   #'IO7        CS',
    'IO4  TX  MISO',
    'IO5  RX    CS',
    'IO6      SCLK',
    'IO7      MOSI',
  ]
  bits = (
    #   iobit  iopin ddirpin  mode
    BP5BIT(0,     8,     0,    Pin.IN),
    BP5BIT(1,     9,     1,    Pin.IN),
    BP5BIT(2,    10,     2,    Pin.IN),
    BP5BIT(3,    11,     3,    Pin.IN),
    BP5BIT(4,    12,     4,    Pin.IN),
    BP5BIT(5,    13,     5,    Pin.IN),
    BP5BIT(6,    14,     6,    Pin.IN),
    BP5BIT(7,    15,     7,    Pin.IN),
  )

  I2C_SDA = bits[0] 
  I2C_SCL = bits[1] 
  UART_TX = bits[4]
  UART_RX = bits[5]
  #SPI_SCLK = bits[4]
  #SPI_MOSI = bits[5]
  #SPI_MISO = bits[6]
  #SPI_CS = bits[7]
  SPI_MISO = bits[4]
  SPI_CS   = bits[5]
  SPI_SCLK = bits[6]
  SPI_MOSI = bits[7]

  def __init__(self, sr):
    self.sr = sr

  def pullups( self, enable = None ):
    if enable is not None:
      if enable:
        self.sr.clr_bit( self.sr.PULLUP_EN )
        self.sr.send()
      else:
        self.sr.set_bit( self.sr.PULLUP_EN )
        self.sr.send()
    # return state of pullups
    # note negative logic
    return not self.sr.get_bit(self.sr.PULLUP_EN)


  def strings(self):
    out = []
    pups = not bool(self.sr.get_bit(self.sr.PULLUP_EN))
    string = 'enabled' if pups else 'disabled'
    for bit in self.bits:
      out.append( f'{bit}' )
    out.append(f'Pullups {string}')
    return out

  def __repr__(self):
    return '\n'.join( self.strings() )

  def __str__(self):
    return '\n'.join( self.strings() )

  def pinout(self):
    return '\n'.join( self.pinout_strings() )


# There are two UARTs, UART0 and UART1. 
# UART0 can be mapped to GPIO 0/1, 12/13 and 16/17, and 
# UART1 to GPIO 4/5 and 8/9.

  def make_uart(self, baudrate=115200):
    self.tx = self.UART_TX
    self.rx = self.UART_RX
    self.tx.mode(Pin.OUT)
    self.rx.mode(Pin.IN)
    self.uart = UART( 0, baudrate, 
                   tx=self.tx.pin,
                   rx=self.rx.pin, )
    return self.uart

  def make_spi(self, baudrate=1_000_000 ):
    self.sclk = self.SPI_SCLK
    self.mosi = self.SPI_MOSI
    self.miso = self.SPI_MISO
    self.cs   = self.SPI_CS
    self.sclk.mode(Pin.OUT)
    self.mosi.mode(Pin.OUT)
    self.miso.mode(Pin.IN)
    self.cs.mode(Pin.OUT)
    self.spi = SPI(1, baudrate, 
       sck=self.sclk.pin,
       mosi=self.mosi.pin,
       miso=self.miso.pin,
    )
    return self.spi
