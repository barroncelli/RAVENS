# simple test to see if mpl3115a2 altimeter can rx/tx with Raspberry Pi
# one known fault of the following is if certain pins, like the Vin pin,
# fall out, the mpl temporarily has enough charge to give back the
# success signal 

import smbus2
import sys

bus = smbus2.SMBus(1)
address = 0x60


# go to "who am I" register on mpl
try:
	device_id = bus.read_byte_data(address, 0x0C)
except OSError:
	print("\nerror:")
	print(OSError)
	print("\nConfirm all wire connections are secure!\n")
	sys.exit(1)

if device_id == 0xC4:
	print("Success! Sensor detected.")
else:
	print(f"Returned {hex(device_id)} instead")



