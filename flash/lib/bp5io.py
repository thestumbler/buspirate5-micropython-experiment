from machine import Pin, UART, SPI

class BP5BIT:
  __doc__ = \
  '''Manages one I/O connector signal bit.
  bit = BP5BIT( IOBIT, PIN_NUM_IO, PIN_NUM_DIR, DIRECTION, PULL)
    where:
      IOBIT        bit number (0..7)
      PIN_NUM_IO   BP5 signal pin number (8..15)
      PIN_NUM_DIR  BP5 direction pin number (0..7)
      DIRECTION    Pin.IN or Pin.OUT
      PULL         Pin.PULL_UP, Pin.PULL_DOWN, None
  Class functions:
    mode(dir, pull)  (re-)configures pin mode
    value()          gets the pin value
    value(val)       sets the pin value
    on()             pin on (high)
    off()            pin off (low)'''

  def help(self):
    print(self.__doc__)

  def dir_string( self, d ):
    if   d == Pin.IN:         return '0=INPUT     '
    elif d == Pin.OUT:        return '1=OUTPUT    '
    elif d == Pin.OPEN_DRAIN: return '2=OPEN_DRAIN'
    return                          f'{d}=UNKNOWN   '

  def pull_string( self, p ):
    if p is None:              return 'None=No pulls'
    else:
      if   p == Pin.PULL_UP:   return '1=PULL_UP    '
      elif p == Pin.PULL_DOWN: return '2=PULL_DOWN  '
      return                          f'{d}=UNKNOWN '

  def __init__(self, iobit, pin_num_io, pin_num_dir, 
               direction, pull=Pin.PULL_UP):
    self.iobit = iobit
    self.pin_num_dir = pin_num_dir
    self.pin_num_io = pin_num_io
    self.dir = Pin( self.pin_num_dir, Pin.OUT ) 
    self.mode(direction, pull)

  def mode(self, direction, pull=Pin.PULL_UP):
    self.direction = direction
    self.pull = pull
    self.pin = Pin( self.pin_num_io, self.direction, self.pull )
    if self.direction == Pin.OUT:
      self.dir.on()
    else:
      self.dir.off()

  def __repr__(self):
    return \
    f'IO.{self.iobit}: ' \
    f'GPIO{self.pin_num_io:02d} V:{self.pin.value()} ' \
    f'D:{self.dir_string(self.direction)}        ' \
    f'P:{self.pull_string(self.pull)}          ' \
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
  __doc__ = \
  '''Manages the I/O connector signals.
  io = BP5IO( SR )
    where:
      SR           shift register class
  Class functions:
    pullups(en)    enable/disable BP5 global pullups
    cheat()        display I/O pin cheat sheet on display
    make_uart()    returns UART object after setting pins
      port         0 or 1, default = 0
      baudrate     baudrate, default = 115200 Bd
    make_spi()     returns SPI object after setting pins
      baudrate     clock rate, default = 1 MBd
  Class members:
    bits[0-7]      BP5BIT instances, one per bit'''

  def help(self):
    print(self.__doc__)

  pinout_cheat_sheet = [
    '         VREG',
    'IO0  SDA  TX1',
    'IO1  SCL  RX1',
    'IO2          ',
    'IO3          ',
   #'IO4  TX  SCLK', # BP5 original pinouts for SPI
   #'IO5  RX  MOSI', # can't use with default RP2040
   #'IO6      MISO',
   #'IO7        CS',
    'IO4  TX0 MISO',
    'IO5  RX0   CS',
    'IO6      SCLK',
    'IO7      MOSI',
    '          GND',
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
  UART_TX0 = bits[4]
  UART_RX0 = bits[5]
  UART_TX1 = bits[0]
  UART_RX1 = bits[1]
  #SPI_SCLK = bits[4]
  #SPI_MOSI = bits[5]
  #SPI_MISO = bits[6]
  #SPI_CS = bits[7]
  SPI_MISO = bits[4]
  SPI_CS   = bits[5]
  SPI_SCLK = bits[6]
  SPI_MOSI = bits[7]

  def __init__(self, sr, disp):
    self.sr = sr
    self.disp = disp

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

  def cheat(self):
    """Show I/O pin definitions on the screen"""
    self.disp.cls()
    for row, pinout in enumerate(self.pinout_cheat_sheet):
      print(pinout)
      self.disp.text( pinout, row+1, 0 )
  


# There are two UARTs, UART0 and UART1,
# which can be mapped as follows:
# UART0 to GPIOs 0/1, 12/13 and 16/17
# UART1 to GPIOs 4/5 and 8/9
#
# port 0 (GPIO 12/13)    BP5 normal uart
# port 1 (GPIO 8/9)      unique to this demo

  def make_uart(self, port=0, baudrate=115200):
    if port == 0:
      self.tx = self.UART_TX0
      self.rx = self.UART_RX0
    elif port == 1:
      self.tx = self.UART_TX1
      self.rx = self.UART_RX1
    else:
      raise RuntimeError(f"Invalid UART port {port}, must be 0 or 1")
    self.port = port
    self.tx.mode(Pin.OUT)
    self.rx.mode(Pin.IN)
    self.uart = UART( self.port, baudrate, 
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




