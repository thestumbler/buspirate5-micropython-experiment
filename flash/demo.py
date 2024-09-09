from machine import Pin, SPI
import time
from bp5pins import *
import buspirate5
import eeprom_spi as eeprom
from hexdump import hexdump

# Simple demonstration classes for the hardware interfaces.

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


class UART:
  def __init__( self, bp, port=0, baud=115200 ):
    self.bp = bp
    self.port = port
    self.baud = baud
    self.initialized = False

  def init(self):
    self.uart = self.bp.io.make_uart(self.port, self.baud)
    self.initialized = True

    # uart.write('hello world\r\n')
    # line = uart.readline()
    # print(line)
    # uart.write(line)




