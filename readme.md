# MicroPython on Bus Pirate 5 -- Experimental Proof of Concept

This repo contains MicroPython (MP) modules for use in exercising the
hardware and interfaces of the using the RP2040 microcontroller based
Bus Pirate 5 (BP5) from Dangerous Prototypes.

These modules are not intended to be a replacement for the C-based
native BP5 firmware. Instead, they are an simply alternate means of 
operating with the BP5 from MicroPython rather than the command line. 

NOTE: This code is experimental, and still has problems ( see below ). 
Do not use it for anything important.

## Installation

* clone this project
* program the BP5 with Micropython (see below)
* copy flash directory to the BP5 

## Project Folder Organization

```
|-- bin             <== project related scripts, progs
|-- datasheets      <== various datatsheets
|-- docs            <== misc documents, spreadsheets, etc.
|-- ext             <== external libraries, submodules
|   |-- micropython_eeprom
|   |-- spi_flash
|   +-- st7789_mpy
|-- flash           <== files to upload to BP5
|   |-- examples
|   |-- fonts
|   +-- lib
+-- micropython     <== BP5 board description file
    +-- ports           for MicroPython, optional
        +-- rp2
            +-- boards
                +-- BUS_PIRATE5
```

## Project Files on Flash Drive

```
flash
|-- boot.py            <== standard MP bootup
|-- main.py            <== main program
|-- demo.py            <== contains some demo programs
|-- lib
|   |-- buspirate5.py
|   |-- bp5pins.py     <== RP2040 pin definition constants
|   |-- bp5io.py       <== Manages BP5 I/O pins and devices
|   |-- sr595.py       <== on-board I/O expansion shift register
|   |-- lamps.py       <== BP5 board ring multicolor LEDs
|   |-- analog.py      <== manages analog-to-digital converters
|   |-- display.py     <== controls the BP5 OLED display
|   |-- power.py       <== adjustable power supply / current limiter
|   |-- splash.py      <== splash screen on TFT
|   |-- nand.py        <== nand flash driver (not working)
|   |-- eeprom_spi.py  <== eeprom driver code (EXT1)
|   |-- bdevice.py     <== block device driver (EXT1)
|   |-- flash_spi.py   <== spi flash driver code (EXT1)
|   |-- flash_test.py  <== flash utility functions (EXT1)
|   |-- spiflash.py    <== spi flash driver code (EXT2)
|   |-- flashbdev.py   <== block device driver (EXT2)
|   |-- st7789py.py    <== OLED driver code (EXT3)
|   |-- hexdump.py     <== block hex dump utility
```

## Micropython

These modules will work with the default v1.24 MicroPython build for the
Raspberry Pi RP2040 Pico.  There is a MicroPython board definition
folder in this repository BUS_PIRATE5 for making a custom MP build.
Note: Testing with the default Thonny MicroPython to install MP failed.
It seems that the code fails when run under v1.23 of MP. 

#### Local FLASH drive size

I attempted to make MP make use of the full capacity of the
RP2040-connected 16 MiB QSPI NOR flash.  There is a standard MicroPython
setting for specifying a portion of the QSPI flash to be used for the
local flash drive. 

```
Pico RP2040:    Winbond W25Q16JV       16 Mib / 2 MiB
Bus Pirate 5:   Winbond W25Q128JV      128 Mib / 16 MiB
```

When I tried to increaase the size of the flash drive to 8 MB as a quick
test, the build failed. It turns out there is a 2 GB hard-limit in the
Pico-SDK.  Exceeding that requires an edit to a Pico-SDK file, and maybe 
a re-compilation of the SDK. I decided to skip this and just live with
the default 1.4 GB flash drive for now.

```
#define MICROPY_HW_FLASH_STORAGE_BYTES          (1408 * 1024)
// #define MICROPY_HW_FLASH_STORAGE_BYTES          (8 * 1024 * 1024)
```

#### Doc Strings and Help

Since this is meant to be a demo, and be convenient to run from the
REPL, I wanted to add help to all the modules and functions. To save
memory, doc strings are disabled default. There is configuration
parameter to enable doc strings. However, it turns out there the help()
function doesn't process doc strings like on the desktop. So this switch
turns out to be not very helpful.

```
// Whether to include doc strings (increases RAM usage)
#define MICROPY_ENABLE_DOC_STRING (1)
```

#### Pinouts

```
   BP5       BP5-firmware        MicroPython
   I/O            defined            project
   Pin            pinouts            pinouts 
  =====      =============      =============
   IO0                SDA        TX1*    SDA   
   IO1                SCL        RX1*    SCL   
   IO2                                         
   IO3                                         
   IO4        TX     SCLK        TX0    MISO*
   IO5        RX     MOSI        RX0      CS*
   IO6               MISO               SCLK*
   IO7                 CS               MOSI*

```

The BP5 C-based firmware uses RP2040 PIO programming for the 
interfaces. MicroPython supports PIO programming as well, but I didn't
want to go down that route on this project.  Instead, I used the normal
I/O peripheral support built into MP.  For the most part, these line up
with the pin definitions of the BP5 firmware, except that the SPI port
is arranged differently. A second UART is provided for convenience and 
loopback testing.

BP5 hardware requires I/O direction control (GPIO pins 0-7). The
direction is static for UART and SPI ports. But is dynamic for I2C 
ports, and therefore I did not include it in this initial release.
Porting existing BP5 PIO code into MicroPython will solve this.

#### NAND Flash

The Micron MT29F1G01AB, 1 Gib / 128 MiB, SPI-connected NAND flash memory
is not currently supported. Several attempts were made to access
this memory using a couple of standard libraries without success.
Getting this to work is just a matter of additional time and focus.

## Libraries

* MicroPython drivers for memory chips, Peter Hinch
  - [https://github.com/peterhinch/micropython_eeprom](https://github.com/peterhinch/micropython_eeprom)

* SPI Block Device Driver, Robert Hammelrath
  - [https://github.com/robert-hh/SPI_Flash](https://github.com/robert-hh/SPI_Flash)

* MicroPython LCD Driver in Python, Russ Hughes
  - [https://github.com/russhughes/st7789py_mpy](https://github.com/russhughes/st7789py_mpy)


## Bus Pirate 5

* [https://hardware.buspirate.com/introduction](https://hardware.buspirate.com/introduction)
* [https://github.com/DangerousPrototypes/BusPirate5-firmware](https://github.com/DangerousPrototypes/BusPirate5-firmware)
* [https://github.com/DangerousPrototypes/BusPirate5-hardware](https://github.com/DangerousPrototypes/BusPirate5-hardware)

## Micropython

* [https://github.com/micropython/micropython](https://github.com/micropython/micropython)
* [https://docs.micropython.org/en/latest/index.html]()
