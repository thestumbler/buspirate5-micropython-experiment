from machine import Pin, SPI
import time
from bp5pins import *
import buspirate5
import eeprom_spi as eeprom
from hexdump import hexdump
import demo 

bp = buspirate5.BP5()

msg = bytearray(b'The quick brown fox jumped over the lazy dog.') 

# ee = demo.EEPROM( bp )

# u0 = demo.UART( bp, 0 )
# u1 = demo.UART( bp, 1 )

def loopback_string( xmt, rcv, string, nloops=10 ):
  for iloop in range(nloops):
    print(f'Looping {xmt.port}>>>{rcv.port}, test {iloop:>3d}:  ', end='')
    for ch in msg:
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


def loopback():
  u0.init()
  u1.init()
  loopback_string(u0,u1,msg)
  loopback_string(u1,u0,msg)


    
