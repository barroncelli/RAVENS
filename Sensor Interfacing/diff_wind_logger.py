# The diff_wind_logger program takes in simultaneous pressure readings
# from a BME680 pitot tube pressure sensor

import board
import busio
import adafruit_mpl3115a2
import adafruit_bme680
import time
import numpy as np
import csv
import os
import datetime


dt = .05  # sensing period

i2c = busio.I2C(board.SCL, board.SDA)

mpl = adafruit_mpl3115a2.MPL3115A2(i2c)
bme = adafruit_bme680.Adafruit_BME680_I2C(i2c)

bme.filter_size = 0 # disable the internal low-passing
# because this introduces hysteresis in pressure data

# we can also increase redundancy:
# bme.pressure_oversample = 2 

# sea level pressure unimportant for diff_pressure readings
#sealevel_p = 1013.25 # make this dynamic later
#bme.sea_level_pressure = sealevel_p
#bno.sea_level_pressure = sealevel_p


timestamp = time.strftime("%Y%m%d-%H%M%S")
folder = "wind captures"
filename = f"dw_log_{timestamp}.csv"
filepath = os.path.join(folder,filename)
file_exists = os.path.isfile(filepath)
print(f"Logging baro1/baro2/dp/wind data to {filename}. Ctrl+C to stop.")



with open(filepath, mode='a', newline = '') as csvfile:
	fieldnames = ['timestamp', 'pressure_mpl', 'pressure_bme', 'diff_pressure', 'v_wind_est']
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

	# headers at top of csv:
	if not file_exists:
		writer.writeheader()

	try:
		while True:
			pbme = bme.pressure # pitot pressure
			pmpl = mpl.pressure # environment pressure
			pbme = float(pbme)
			pmpl = float(pmpl)
			dp = 100 * (pbme-pmpl) # hPa to Pa
			
			temp = float(bme.temperature)
			hum = float(bme.humidity)
			hum = hum/100 # convert from pct to decimal
			
			pascal = pmpl*100 # environment pressure in pascal
			
			#hum = humidity pct from BME
			#temp = temp in celsius from BME
			#pascal = pressure in pascals from MPL
			
			pvapor = hum*610.78*np.exp((17.27*temp)/(temp+237.3))
			ctk = temp+273.15
			rho = (pascal-pvapor)/(287.058*ctk) + (pvapor)/(461.5*ctk)

			
			# By Bernoulli's eqn, v = sqrt((2*dp)/rho), units m/s
			
			vwind = np.sqrt((2*abs(dp))/rho) 
			if dp < 0:
				vwind = -vwind
			
			cur = datetime.datetime.now()
			
			t = time.strftime("%Y-%m-%d %H:%M:%S") + f".{cur.microsecond//1000:03d}"
			writer.writerow({
			
				'timestamp': t,
				'pressure_mpl': f"{pmpl:.2f}",
				'pressure_bme': f"{pbme:.2f}",
				'diff_pressure': f"{dp:.2f}",
				'v_wind_est': f"{vwind:.2f}"
			})
			#print(hum)
			#print(rho)
			print(f"{t} | pmpl: {pmpl:.2f}hPa | pbme: {pbme:.2f}hPa | dp: {dp:.2f}hPa | vwind = {vwind:.2f}")
			csvfile.flush()
			time.sleep(dt)

	except KeyboardInterrupt:
			print("\nLogging stopped.")





