import time
import buspirate5

time.sleep_ms(500)

bp = buspirate5.BP5()
b = bp

__doc__ = \
    '''For help:
BP5         bp.help()      main Bus Pirate 5 
Lamps       lamps.help()   BP5 board ring multicolor LEDs
Display     disp.help()    controls BP5 OLED display
BP5IO       io             manages BP5 I/O pins and devices
Analog      adc            manages analog-to-digital converters
Power       psu            adjustable power supply / current limiter
Pin         sw2            user push button'''
print(__doc__)

from demo_uart import ugo
ugo() # show help message

from demo_eeprom import ego
ego() # shows help message

from demo_io import igo
igo() # shows help message

