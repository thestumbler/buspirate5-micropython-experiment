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

* program the BP5 with Micropython

* copy flash directory to the BP5 

## Project File / Class Organization 

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

## Files on Flash Drive

```
flash
|-- boot.py            <== standard MP bootup
|-- main.py            <== main program
|-- demo.py            <== contains some demo programs
|-- lib
|   |-- buspirate5.py
|   |-- bp5pins.py
|   |-- bp5io.py
|   |-- sr595.py
|   |-- lamps.py
|   |-- st7789py.py
|   |-- analog.py
|   |-- display.py
|   |-- power.py
|   |-- eeprom_spi.py
|   |-- bdevice.py
|   |-- flash_spi.py
|   |-- flash_test.py
|   |-- spiflash.py
|   |-- flashbdev.py
|   |-- hexdump.py
|   |-- nand.py
|-- examples
|   |-- boxlines.py
|   |-- color_test.py
|   |-- feathers.py
|   +-- hello.py
+-- fonts
```


## Using the Modules

## Issues

#### Pinouts

#### NAND Flash




## Libraries

MicroPython drivers for memory chips
https://github.com/peterhinch/micropython_eeprom

SPI Block Device Driver
https://github.com/robert-hh/SPI_Flash

MicroPython LCD Driver in Python
https://github.com/russhughes/st7789py_mpy


## Bus Pirate 5

https://hardware.buspirate.com/introduction
https://github.com/DangerousPrototypes/BusPirate5-firmware
https://github.com/DangerousPrototypes/BusPirate5-hardware

## Micropython

https://github.com/micropython/micropython
https://docs.micropython.org/en/latest/index.html

