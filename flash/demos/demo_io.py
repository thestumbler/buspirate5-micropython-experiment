from machine import Pin, SPI
import time
from bp5pins import *
import buspirate5
from hexdump import hexdump

# Simple demonstration of IO pins

def igo( bp=None ):
  __doc__ = \
  '''I/O demo igo() command
  igo()       shows this help message
  igo(bp)     runs the EEPROM demo, bp argument is BP5'''

  if bp is None:
    print(__doc__)
    return

  print('I/O bits demo (press SW2 to quit) ...')

  print('  set IO bits 0-3 as outputs ...')
  for i in range(0,4):
    bp.io.bits[i].mode( Pin.OUT )
    print(f'    {bp.io.bits[i]}')
  print('  set IO bits 4-7 as inputs ...')
  for i in range(4,8):
    bp.io.bits[i].mode( Pin.IN )
    print(f'    {bp.io.bits[i]}')

  # memory
  olast = [None]*4
  ilast = [None]*4
  
  bp.io.print(clear=True, display=True, console=False)
  count = 0
  while( True ):
    # set the output nibble bit pattern ...
    for ibit in range(0,4):
      bit = bp.io.bits[ibit]
      val = (count >> ibit) & 0x01
      bp.io.bits[ibit].value(val)
      # print any that have changed
      if olast[ibit] is None or ( val != olast[ibit] ):
        bp.io.print_bit( ibit, display=True, console=False)
        olast[ibit] = val

    # check the intput nibble
    for ibit0 in range(0,4):
      ibit4 = ibit0+4
      val = bp.io.bits[ibit4].value()
      if ilast[ibit0] is None or ( val != ilast[ibit0] ):
        bp.io.print_bit( ibit4, display=True, console=False)
        ilast[ibit0] = val

    time.sleep_ms(250)
    count = count + 1
    if bp.sw2(): break

  bp.splash()



