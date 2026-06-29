import time
import board
import busio
import adafruit_mpl3115a2
import csv
import os
import sys
import subprocess
import datetime


dt = .05  # sensing period

i2c = busio.I2C(board.SCL, board.SDA)

# call the test_sensor func to ensure i2c is behaving
result = (subprocess.run(["python3", "test_mpl.py"],
		  capture_output = True, text=True))
		  
test_sensor_output = result.stdout

# one known fault of the following is if certain pins, like the Vin pin,
# fall out, the mpl temporarily has enough charge to give back the
# success signal 

if not ("Success! Sensor detected.") in test_sensor_output:
	print(test_sensor_output)
	sys.exit(1)
		  

sensor = adafruit_mpl3115a2.MPL3115A2(i2c)
sensor.sealevel_pressure = 1021.59  # in the future, I will make this
				# an inputable reference point
				
#sensor.pressure_osr = 1 # change oversampling rate to increase datapoints per sec

timestamp = time.strftime("%Y%m%d-%H%M%S")

folder = "mpl captures"
filename = f"mpl_log_{timestamp}.csv"
filepath = os.path.join(folder,filename)
file_exists = os.path.isfile(filepath)
print(f"Logging barometric/altimeter/temperature data to {filename}. Ctrl+C to stop.")

with open(filepath, mode='a', newline = '') as csvfile:
	fieldnames = ['timestamp', 'altitude_m', 'pressure_hPa', 'temp_c']
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

	# headers at top of csv:
	if not file_exists:
		writer.writeheader()

	try:
		while True:
			alt = sensor.altitude
			#pres = sensor.pressure
			#temp = sensor.temperature
			cur = datetime.datetime.now()
			
			t = time.strftime("%Y-%m-%d %H:%M:%S") + f".{cur.microsecond//1000:03d}"
			writer.writerow({
				'timestamp': t,
				'altitude_m': f"{alt:.2f}"#,
				#'pressure_hPa': f"{pres:.2f}",
				#'temp_c': f"{temp:.2f}"
			})

			print(f"{t} | Alt: {alt:.2f}m")
			
			#print(f"{t} | Alt: {alt:.2f}m | Pressure: {pres:.2f}hPa | Temp: {temp:.2f}")
			csvfile.flush()
			time.sleep(dt)

	except KeyboardInterrupt:
			print("\nLogging stopped.")
