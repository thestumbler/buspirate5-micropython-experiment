from machine import Pin, SPI
import time
from bp5pins import *
import buspirate5
from hexdump import hexdump

# Simple demonstration of UART

class UART:
  '''Test of serial port UART.'''
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

def loopback_string( xmt, rcv, string, nloops=10 ):
  for iloop in range(nloops):
    print(f'  loopback {xmt.port} to {rcv.port},  num {iloop:>3d}:  ', end='')
    for ch in string:
      xmt.uart.write(bytearray([ch]))
      while not xmt.uart.txdone():
        pass
      loopback = rcv.uart.read()
      if loopback is not None:
        if len(loopback)==1:
          # just got one character back
          if chr(ch) == chr(ord(loopback)):
            print( f'{chr(ch)}', end='' )
          else: 
            print( f'<{chr(ch)}--{chr(ord(loopback))}>', end='' )
        else:
          # got multiple characters back
          print( f'<{chr(ch)}--{loopback.decode()}>', end='' )
      else: 
        # got nothing back
        print( f'<{chr(ch)}--?>', end='' )
    print()


def ugo( bp=None ):
  __doc__ = \
  '''UART demo ugo() command
  ugo(bp)     runs the EEPROM demo, bp argument is BP5
  ugo()       shows this help message'''

  if bp is None:
    print(__doc__)
    return

  msg = bytearray(b'The quick brown fox jumped over the lazy dog.') 

  u0 = UART( bp, 0 )
  u1 = UART( bp, 1 )
  u0.init()
  u1.init()

  print('Running UART Demo ...')
  loopback_string(u0, u1, msg)
  loopback_string(u1, u0, msg)

