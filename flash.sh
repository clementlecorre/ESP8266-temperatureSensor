#!/bin/bash
esptool.py --port /dev/tty.SLAB_USBtoUART erase_flash
python3 ./esptool.py --port /dev/cu.SLAB_USBtoUART write_flash --flash_size=detect 0 esp8266-20171101-v1.9.3.bin
