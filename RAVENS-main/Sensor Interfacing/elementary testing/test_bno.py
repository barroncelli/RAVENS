# simple test to see if bno055 IMU can rx/tx with Raspberry Pi
# If the Vin pin falls out, the bno temporarily has enough charge to send
# a success signal before dying

import smbus2
import sys

bus = smbus2.SMBus(1)
address = 0x28

# call the "who am I" register for bno

try: 
	device_id = bus.read_byte_data(address, 0x00) #are you alive ping
except OSError:
	print("\nerror:")
	print(OSError)
	print("\nConfirm all wire connections are secure.\n")
	sys.exit(1)

if device_id == 0xA0:
	print("Success! Sensor detected.")
else:
	print(f"Returned {hex(device_id)} instead")
