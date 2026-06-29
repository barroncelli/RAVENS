# pswib_log.py logs time-indexed power, speed, wind, imu, 
# and barometric data to CSV
# This file is an accumulation of work from the following files:
#
# To prevent obscene latency, ensure I2c clock is maxed out at 400khz
#
# reedspeed_logger.py
# bno_logger.py
# diff_wind_logger.py
# ble_pwr_logger.py
#
#
# datafields: 
#
# no sensor: timestamp
# speed sensor: speed, time elapsed since last speed update
# 		-> will care more about extrapolated speed, this can be logged
# handlebar-mounted BME680: pressure
# framebag-mounted BME680: pressure
#		-> these two will also measure temp+hum and give us:
#          differential pressure, computed windspeed
# bottom bracket-mounted BNO055: XYZ acceleration, XYZ gyro
# powermeter: instantaneous power
#
# Note: some of these readings need be less frequent than others.
#
# Logging humidity or extrapolated speed at same fs 
# as acceleration data is not useful.


### ADD: rho, last update bme1, last update bme2, last update bno, power, speed
### also update speed for multiple magnets

import csv
import time
import os
import board
import busio
import sys
import subprocess
import numpy as np
import datetime

#IMU:
import adafruit_bno055
import json
# reedspeed:
from gpiozero import Button
# Baro:
import adafruit_bme680
# Powermeter:
import asyncio
import struct
from bleak import BleakClient
import threading


dt = .01

# speed sensor GPIO pin:
gpio_s = 26
circum = 2.096	# inflated tire circumference in m
min_speed = .4469 # below this in m/s, we want speed readout=0

address = "EF:79:3C:65:6E:8E" # address for my own powermeter
# if you want a quick scare to see how many bluetooth devices are 
# running around you, you can run :
# sudo hcitool lescan
# and watch all the devices pop up
uuid = "00002a63-0000-1000-8000-00805F9B34FB"


i2c = busio.I2C(board.SCL, board.SDA)

timestamp = time.strftime("%Y%m%d-%H%M%S")
folder = "full captures"
filename = f"full_log_{timestamp}.csv"
filepath = os.path.join(folder,filename)
file_exists = os.path.isfile(filepath)


bno = adafruit_bno055.BNO055_I2C(i2c)
bno.mode = adafruit_bno055.CONFIG_MODE #allow to be configured now

# first, load json file with calibration info
with open("bno calibration/bno055_offsets.json", "r") as f:
		config = json.load(f) # dict of all the data
bno.offsets_accelerometer = tuple(config["offset_a"])
bno.offsets_gyroscope = tuple(config["offset_g"])
bno.offsets_magnetometer = tuple(config["offset_m"])
bno.radius_accelerometer = config["radius_a"]
bno.radius_magnetometer = config["radius_m"]
bno.mode = adafruit_bno055.IMUPLUS_MODE # collect accel, gyro data

# coordinate rotation matrix, computed in RAVENS/Processing/coordinate_conv.py

R = np.array([[ 9.99312675e-01,  4.33680869e-19, -3.70699121e-02],
 [ 3.13222584e-03,  9.96423895e-01,  8.44370220e-02],
 [ 3.69373462e-02, -8.44950976e-02,  9.95739028e-01]])

last_a = np.array([0,0,9.71]) # coords for my stationary bno
last_g = np.array([0,0,0])
imulock = threading.Lock()
last_imu_ping = time.monotonic()
def imu_ping():
	global last_a, last_g, last_imu_ping
	# could add try/except to prevent i2c issue from derailing whole file
	while True:
                this_acc = bno.acceleration
                if this_acc != a:
                    last_imu_ping = time.monotonic()
		a = this_acc
		g = bno.gyro
		if  a[0] is not None and g[0] is not None:
					   # this occasional glitchy misread as None 
					   # puts a stop to the entire program
			a_mapped = a@R
			g_mapped = g@R
			with imulock:
				last_a = a_mapped
				last_g = g_mapped
		time.sleep(.001)

imu_thread = threading.Thread(target=imu_ping, daemon=True)
imu_thread.start()
	

bme = adafruit_bme680.Adafruit_BME680_I2C(i2c, address=0x77)
bme.filter_size = 0 # adjust the internal low-passing
# to balance consistency and hysteresis in pressure data
bme.pressure_oversample=4
bme._run_gas = False # we don't need gas analytics

last_pbme = bme.pressure
last_tbme = bme.temperature
last_hbme = bme.humidity
bmelock = threading.Lock()
bme_last_ping = time.monotonic()
def bme_ping():
	global last_pbme, last_tbme, last_hbme, bme_last_ping
	counter = 0
	while True:
		pbme = float(bme.pressure) # pitot pressure
		if pbme != last_pbme:
                    bme_last_ping = time.monotonic()
		counter += 1
		with bmelock:
			last_pbme = pbme
			if counter % 10 == 0: # decrease latency by sampling less
				last_tbme = float(bme.temperature)
				last_hbme = float(bme.humidity)
		time.sleep(.001)
bme_thread = threading.Thread(target=bme_ping, daemon=True)
bme_thread.start()
			
	
#second pressure sensor in bag for wind calcs 
bag_bme = adafruit_bme680.Adafruit_BME680_I2C(i2c, address=0x76)
bag_bme.filter_size = 0
bag_bme.pressure_oversample=4
bag_bme.temperature_oversampling=16
bag_bme.humidity_oversampling=16
bag_bme._run_gas = False

last_bag = 0
baglock = threading.Lock()
bag_last_ping = time.monotonic()
def bag_ping():
	global last_bag, bag_last_ping
	while True:
		pbag = float(bag_bme.pressure) # environmental pressure
		with baglock:
                    if last_bag != pbag: # catches each new ping
                        bag_last_ping = time.monotonic()
                    last_bag = pbag
		time.sleep(.001)
bag_thread = threading.Thread(target=bag_ping, daemon=True)
bag_thread.start()

		
# number of samples to calibrate the offsets between sensors:
calibrate_size = 100
pbme_logs = []
pbag_logs = []
while len(pbme_logs) < calibrate_size:
	if last_pbme > 0 and last_bag > 0:
		with bmelock:
			pbme_logs.append(last_pbme)
		with baglock:
			pbag_logs.append(last_bag)
		time.sleep(.01)
pbme_avg = np.mean(pbme_logs)
pbag_avg = np.mean(pbag_logs)
delta_bme = pbme_avg-pbag_avg


#
# speed sensor code:
#
# allow RPi to read gpio pin:
os.environ['GPIOZERO_PIN_FACTOR'] = 'lgpio'
class reedswitch:
	def __init__(self, gpioPin, circumference, minspeed):
		self.switch = Button(gpioPin, pull_up=True, bounce_time=.01)
		# can't be triggered twice within .01s
		self.circumference = circumference
		self.dist_per_dt = circumference / 4 ## 4 MAGNETS PER WHEEL HERE
		self.recent = time.monotonic()
		self._speed = 0.0 # float speed
		self.switch.when_pressed = self.closed_alert
		self.threshold = minspeed #.4469m/s = 1mph, below this readout we want 0
		
	@property
	def speed(self):
		now = time.monotonic()
		d_t = now - self.recent
		d_t_threshold = self.circumference/self.threshold
		if d_t > d_t_threshold:
			self._speed = 0.0 # if sensor hasn't triggered in a while
		return self._speed
	@property
	def elapsed_since_ping:
            return time.monotonic()-self.recent()
	def closed_alert(self):
		now = time.monotonic()
		d_t = now - self.recent
		d_t_threshold = self.circumference/self.threshold
		self._speed = self.dist_per_dt/d_t
		self.recent = now #back to next cycle
instance = reedswitch(gpio_s, circum, min_speed)
#
# end of speed code
#


# powermeter code:
#
power = 0 # before call is made from main csv logging loop
powerlock = threading.Lock()
last_pwr_ping = time.monotonic()
def BLE_ping(pwm, data):
	global power, last_pwr_ping
	new_power = struct.unpack('<h', data[2:4])[0] # '<' to read backwards, 
	last_pwr_ping = time.monotonic()				# H = hex b/c 2 bytes or 16 bit
	with powerlock:
		power = new_power
		
async def BLE_manage(): # should run regardless of BLE ping timing
	pwm = BleakClient(address)
	while True:
		try:
			async with pwm:
				await pwm.start_notify(uuid, BLE_ping) #run ble_ping each ping
				while True:
					await asyncio.sleep(1) #the argument here is arbitrary
		except Exception as e: # not connected yet
			await asyncio.sleep(2) #waits and tries to connect again

def BLE_wrapper():
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	loop.run_until_complete(BLE_manage())
	
# begin async thread and kill with rest of program:
ble_thread = threading.Thread(target=BLE_wrapper, daemon=True)
ble_thread.start()
#
#
# end power code


print(f"Logging power, speed, baro, wind, IMU data to {filename}. Ctrl+C to stop.")


counter = 0
with open(filepath, mode='a', newline = '') as csvfile:

	fieldnames =  ['timestamp', 'pressure_bag', 'pressure_bme', 
				'diff_pressure', 'v_wind_est', 'speed', 
				'accel_x', 'accel_y', 'accel_z',
				'gyro_x', 'gyro_y', 'gyro_z', 'power',
                                'rho', 'since_bno', 'since_bag', 'since_bme',
                               'since_speed', 'since_pwr']
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	
	# headers at top of csv:
	if not file_exists:
		writer.writeheader()
		
	next_sample = time.monotonic()
	start = time.time()
	start_mono = time.monotonic()
	try:
		while True:
			now = time.monotonic()
			sample_timestamp = next_sample # this is what we index data to
			if now < next_sample: # began early
				time.sleep(next_sample-now)
			next_sample += dt
			#
			# wind code:
			#
			with bmelock:
				pbme = last_pbme
				temp = last_tbme
				hum = last_hbme
			
			with baglock:
				pbag = last_bag

                        since_bag = time.monotonic() - bag_last_ping 
			since_bme = time.monotonic() - bme_last_ping
			pbag += delta_bme # pbme and pbag are offset by some amount found above
			dp = 100 * (pbme-pbag) # hPa to Pa
			
			hum = hum/100 # convert from pct to decimal
			
			pascal = pbag*100 # environment pressure in pascal
			
			#hum = humidity pct from BME
			#temp = temp in celsius from BME
			#pascal = pressure in pascals from bag_BME
			
			pvapor = hum*610.78*np.exp((17.27*temp)/(temp+237.3))
			ctk = temp+273.15
			rho = (pascal-pvapor)/(287.058*ctk) + (pvapor)/(461.5*ctk)

			# By Bernoulli's eqn, v = sqrt((2*dp)/rho), units m/s
			
			vwind = np.sqrt((2*abs(dp))/abs(rho)) # rho should always be >0
			# but in first entry due to uninitialized vals can be <0
			if dp < 0:
				vwind = -vwind #tailwind condition
			
			#
			# end wind code
			#
			since_imu = time.monotonic() - last_imu_ping
			with imulock:
				ax = last_a[0]
				ay = last_a[1]
				az = last_a[2]
				gx = last_g[0]
				gy = last_g[1]
				gz = last_g[2]
			
			# reedspeed code:
			speed_now = instance.speed
			elapsed = instance.elapsed_since_ping
			# reedspeed done
			
			# power code:
			with powerlock:
				Pow = power
			since_pwr = time.monotonic - last_pwr_ping
			# power done
			
			
			timestamp = start + (sample_timestamp-start_mono)
			t = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
			writer.writerow({
				'timestamp': t,
				'pressure_bag': f"{pbag:.2f}",
				'pressure_bme': f"{pbme:.2f}",
				'diff_pressure': f"{dp:.2f}",
				'v_wind_est': f"{vwind:.2f}",
				'speed': f"{speed_now:.2f}",
				'accel_x': f"{ax:.2f}",
				'accel_y': f"{ay:.2f}",
				'accel_z': f"{az:.2f}",
				'gyro_x': f"{gx:.2f}",
				'gyro_y': f"{gy:.2f}",
				'gyro_z': f"{gz:.2f}",
				'power': Pow, # no rounding needed
                                'rho': f"{rho:.4f}" # rho is <2 so long decimal
                                'since_imu': f"{since_imu:.2f}",
                                'since_bag': f"{since_bag:.2f}",
                                'since_bme': f"{since_bme:.2f}",
                                'since_speed': f"{elapsed:.2f}",
                                'since_pwr': f"{since)pwr:.2f}"
			})
			
			if counter % 100 == 0:
				csvfile.flush()
			counter += 1
			

			
			
	except KeyboardInterrupt:
		exit()
