from machine import Pin, SPI
import time
from bp5pins import *
import buspirate5
import eeprom_spi as eeprom
from hexdump import hexdump

bp = buspirate5.BP5()


spi = bp.io.make_spi()
ee = eeprom.EEPROM( spi, [bp.io.cs.pin], 1 )
buf = bytearray( b'\x00' * 32 )
ee.readwrite( 0, buf, read=True )
print( hexdump(buf) )



uart = bp.io.make_uart()
uart.write('hello world\r\n')
line = uart.readline()
print(line)
uart.write(line)



