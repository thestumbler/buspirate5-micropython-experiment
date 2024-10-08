# flash_test.py MicroPython test program for Cypress SPI Flash devices.

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2019 Peter Hinch

import uos
import time
from machine import SPI, Pin
from flash_spi import FLASH
from bp5pins import *

# **** ADAPT THIS FUNCTION ****

# Return an EEPROM array. Adapt for platforms other than Pyboard.
# May want to set chip size and baudrate.

device = None
def get_device(_device = None):
  global device
  if device == None:
    if _device == None:
      print("No flash device given")
    else:
      device = _device
      print("Flash device is set")

    # if uos.uname().machine.split(" ")[0][:4] == "PYBD":
    #     Pin.board.EN_3V3.value(1)
    #     time.sleep(0.1)
    # # Adjust to suit number of chips and their wiring.
    # cspins = (Pin(Pin.board.Y5, Pin.OUT, value=1), Pin(Pin.board.Y4, Pin.OUT, value=1))
    # flash = FLASH(SPI(2, baudrate=20_000_000), cspins)
    # print("Instantiated Flash")

    return device

# **** END OF USER-ADAPTED CODE ****

# Dumb file copy utility to help with managing EEPROM contents at the REPL.
def cp(source, dest):
    if dest.endswith("/"):  # minimal way to allow
        dest = "".join((dest, source.split("/")[-1]))  # cp /sd/file /ext/
    with open(source, "rb") as infile:  # Caller should handle any OSError
        with open(dest, "wb") as outfile:  # e.g file not found
            while True:
                buf = infile.read(100)
                outfile.write(buf)
                if len(buf) < 100:
                    break


# ***** TEST OF DRIVER *****
def _testblock(eep, bs):
    d0 = b"this >"
    d1 = b"<is the boundary"
    d2 = d0 + d1
    garbage = b"xxxxxxxxxxxxxxxxxxx"
    start = bs - len(d0)
    end = start + len(garbage)
    eep[start:end] = garbage
    res = eep[start:end]
    if res != garbage:
        return "Block test fail 1:" + str(list(res))
    end = start + len(d0)
    eep[start:end] = d0
    end = start + len(garbage)
    res = eep[start:end]
    if res != b"this >xxxxxxxxxxxxx":
        return "Block test fail 2:" + str(list(res))
    start = bs
    end = bs + len(d1)
    eep[start:end] = d1
    start = bs - len(d0)
    end = start + len(d2)
    res = eep[start:end]
    if res != d2:
        return "Block test fail 3:" + str(list(res))


def test(_eep=None):
    if _eep is None: eep = get_device()
    else: eep = _eep
    sa = 1000
    for v in range(256):
        eep[sa + v] = v
    for v in range(256):
        if eep[sa + v] != v:
            print(
                "Fail at address {} data {} should be {}".format(sa + v, eep[sa + v], v)
            )
            break
    else:
        print("Test of byte addressing passed")
    data = uos.urandom(30)
    sa = 2000
    eep[sa : sa + 30] = data
    if eep[sa : sa + 30] == data:
        print("Test of slice readback passed")

    block = 256
    res = _testblock(eep, block)
    if res is None:
        print("Test block boundary {} passed".format(block))
    else:
        print("Test block boundary {} fail".format(block))
        print(res)
    block = eep._c_bytes
    if eep._a_bytes > block:
        res = _testblock(eep, block)
        if res is None:
            print("Test chip boundary {} passed".format(block))
        else:
            print("Test chip boundary {} fail".format(block))
            print(res)
    else:
        print("Test chip boundary skipped: only one chip!")


# ***** TEST OF FILESYSTEM MOUNT *****
def fstest(format=False, _eep=None):
    if _eep is None: eep = get_device()
    else: eep = _eep
    # ***** CODE FOR LITTLEFS *****
    if format:
        uos.VfsLfs2.mkfs(eep)
    try:
        uos.mount(eep, "/ext")
    except OSError:  # Already mounted
        pass
    print('Contents of "/": {}'.format(uos.listdir("/")))
    print('Contents of "/ext": {}'.format(uos.listdir("/ext")))
    print(uos.statvfs("/ext"))


def cptest(_eep=None):
    if _eep is None: eep = get_device()
    else: eep = _eep
    if "ext" in uos.listdir("/"):
        print("Device already mounted.")
    else:
        try:
            uos.mount(eep, "/ext")
        except OSError:
            print("Fail mounting device. Have you formatted it?")
            return
        print("Mounted device.")
    cp("flash_test.py", "/ext/")
    cp("flash_spi.py", "/ext/")
    print('Contents of "/ext": {}'.format(uos.listdir("/ext")))
    print(uos.statvfs("/ext"))


# ***** TEST OF HARDWARE *****
def full_test(count=10, _flash=None):
    if _flash is None: flash = get_device()
    else: flash = _flash
    for n in range(count):
        data = uos.urandom(256)
        while True:
            sa = int.from_bytes(uos.urandom(4), "little") & 0x3FFFFFFF
            if sa < (flash._a_bytes - 256):
                break
        flash[sa : sa + 256] = data
        flash.sync()
        got = flash[sa : sa + 256]
        if got == data:
            print("Pass {} address {:08x} passed".format(n, sa))
            if sa & 0xFFF > (4096 - 253):
                print("cross boundary")
        else:
            print("Pass {} address {:08x} readback failed.".format(n, sa))
            sa1 = sa & 0xFFF
            print("Bounds {} to {}".format(sa1, sa1 + 256))
            #            flash.sync()
            got1 = flash[sa : sa + 256]
            if got1 == data:
                print("second attempt OK")
            else:
                print("second attempt fail", got == got1)
                for n, g in enumerate(got):
                    if g != data[n]:
                        print("{} {:2x} {:2x} {:2x}".format(n, data[n], g, got1[n]))
            break


helpstr = """Available tests:
test()  Basic hardware test.
full_test(count=10)  Full hardware test, count is no. of passes.
fstest(format=False)  Check or create littlefs filesystem.
cptest()  Copy 2 files to filesystem.
cp()  Primitive copy routine. See docs.
"""
print(helpstr)
