from machine import Pin, SPI
import time
from bp5pins import *
import buspirate5
import eeprom_spi as eeprom
from hexdump import hexdump

# Simple demonstration of SPI EEPROM access

class EEPROM:
  '''Test of Atmel AT25080 8 Kib ( 1024 x 8 ) EEPROM.'''
  SIZE = 1 # kiB
  PAGE = 32 # bytes
  def __init__( self, bp ):
    self.bp = bp
    self.initialized = False

  def __repr__(self):
    out = []
    out.append( f'EEPROM initialized = {self.initialized}')
    if self.initialized:
      out.append( f'  size: {self.prom._c_bytes} KiB' )
    return '\n'.join( out )

  def init(self):
    self.spi = self.bp.io.make_spi()
    self.prom = eeprom.EEPROM( 
              self.spi, [self.bp.io.cs.pin], 
              self.SIZE, page_size=self.PAGE,
              verbose = False,
              addr3=False )
    self.initialized = True
    # parameters for reading / writing data from/to EEPROM
    self.addr = 0
    self.size = 32
    self.buf = bytearray( b'\x55' * self.size )

  def read( self, addr=0, size=32, dump=True ):
    self.addr = addr
    self.size = size
    self.buf = bytearray( b'\x00' * self.size )
    _ = self.prom.readwrite( self.addr, self.buf, read=True )
    if(dump): self.dump()

  def write( self, buf, addr=0, dump=True ):
    self.addr = addr
    self.size = len(buf)
    self.buf = buf
    _ = self.prom.readwrite( self.addr, self.buf, read=False )
    if(dump): self.dump()

  def erase(self, fill=b"\0"):
    self.prom.erase(fill)

  def dump( self ):
    hexdump( self.buf, offset=self.addr )


def ego( bp=None ):
  __doc__ = \
  '''EEPROM demo ego() command
  ego(bp)     runs the EEPROM demo, bp argument is BP5
  ego()       shows this help message'''

  if bp is None:
    print(__doc__)
    return

  msg_list = [ 
    bytearray(b'The quick brown fox jumped over the lazy dog.'),
    bytearray(b'The lazy red fox crawled over the sleepy dog.'),
    bytearray(b'The gloomy blue fox cried over the tired dog.'),
    bytearray(b'The perky yellow fox lept over the happy dog.'),
  ]

  ee = EEPROM( bp )
  ee.init()
  addr_list = [ 0x00, 0x40, 0x80, 0xc0 ]
  fill_list = [ 0xaa, 0x55 ]

  for fill in fill_list:
    print(f'* erase with fill with value test, 0x{fill:02x} ...')
    ee.erase(b'\xaa')
    ee.read(0,256) # read and dump first 256 bytes
    time.sleep_ms(100)

  print('* erase, default fill (0x00)')
  ee.erase()
  ee.read(0, 256) # read and dump first 256 bytes
  time.sleep_ms(100)

  print('* writing some messages ...')
  for addr, msg in zip(addr_list, msg_list):
    print(f'  - msg @ 0x{addr:04x}: {msg.decode("ascii")}')
    ee.write(msg, addr, dump=False)
    time.sleep_ms(100)
    
  print('* reading some messages ...')
  for addr, msg in zip(addr_list, msg_list):
    print(f'  - msg @ 0x{addr:04x}: {msg.decode("ascii")}')
    ee.read(addr, len(msg), dump=False)
    time.sleep_ms(100)

  print('dump of first 256 bytes ...')
  ee.read(0, 256) 

