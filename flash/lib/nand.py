import os
from machine import Pin
import time
from bp5pins import *
from hexdump import hexdump

# ========================================================================
# NOTE: Neither of these two approaches are working ....
# The SPI codes for the Micron NAND flash are too different 
# ========================================================================

# which nand flash driver library to use
PETER_HINCH = False
ROBERT_HAMMELRATH = True
if PETER_HINCH:
  import flash_spi
  from flash_test import *
if ROBERT_HAMMELRATH:
  from flashbdev import FlashBdev
  from spiflash import SPIflash


class NAND:

  # From Micron data sheet
  # * Plane size: 1Gb (1 plane, 1024 blocks per plane)
  # * Block size: 64 pages (128K + 8K bytes)
  # * Page size x1: 2176 bytes (2048 + 128 bytes)

  SEC_SIZE = const(64*1024)   # Micron's block size
  BLOCK_SIZE = 11 # 2 KiB       # Micron's page size
  # Modified scan in flash_spi to recognize this chip
  # and report the correct 1GB size
  SIZE = None 

  SECTOR_SIZE = (136 * 1024)

  def __init__(self, spi):
    self.spi = spi
    self.cs = Pin( PIN_SD_CS, Pin.OUT)
    self.cs(1)
    time.sleep_ms(200)
    if PETER_HINCH:
      self.flash = flash_spi.FLASH( self.spi, 
        [ self.cs ], 
        sec_size = self.SEC_SIZE, 
        block_size = self.BLOCK_SIZE, 
        cmd5=True,
        verbose=True 
      )
    if ROBERT_HAMMELRATH:
      self.flash=SPIflash(
          self.spi, 
          self.cs,
          sectorsize=self.SECTOR_SIZE,
          addr4b=True,
      )
      self.bdev=FlashBdev( self.flash )

  def format(self):
    # # Omit this to mount an existing filesystem
    os.VfsLfs2.mkfs(self.flash)  

  def erase(self):
    self.flash.flash_erase(0)

  def dump(self):
    buf = bytearray(b'\x00' * 128)
    self.flash.flash_read(0, buf)
    hexdump(buf)

  def format2(self):
    try:
      vfs = os.VfsLfs2(self.flash, progsize=256)
    except OSError as e:
      print("Mount failed with error", e)
      print("Recreate the file system")  # Previous content is lost!
      os.VfsLfs2.mkfs(self.flash, progsize=256)
      vfs = os.VfsLfs2(self.flash, progsize=256)

  def mount(self):
    os.mount(self.flash,'/ext')

  def unmount(self):
    os.umount('/ext')

  def list(self):
    print('ROOT DIR:')
    print( '\n'.join( os.listdir() ) )
    print('/EXT:')
    print( '\n'.join( os.listdir('/ext') ) )

  def copy(self):
    cp('boot.py', '/ext/testing.txt')
    cp('main.py', '/ext/woohoo.txt')

#   def test(self):
#     flash_test.test()
# 
#   def full_test(self, count=10):
#     flash_test.full_test(count)
# 
#   def fstest(self,format=False):
#     flash_test.fstest(format)
# 
#   def fstest(self,format=False):
#     flash_test.fstest(format)
# 
#   def cptest(self):
#     flash_test.cptest()
