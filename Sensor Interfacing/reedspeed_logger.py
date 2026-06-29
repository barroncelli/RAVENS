import os
# bootleg fix to RPi bugs:
os.environ['GPIOZERO_PIN_FACTOR'] = 'lgpio'

from gpiozero import Button
import time
import csv
import datetime

# simplest approach was to make reedswitch class
# my reed switch (normally open) is conencted to gpio 26
# 700x23C wheel has 2096mm circumference
class reedswitch:
	def __init__(self, gpioPin=26, circumference=2.096):
		self.switch = Button(gpioPin, pull_up=True, bounce_time=.01)
		# can't be triggered twice within .01s
		self.circumference = circumference
		self.dist_per_dt = circumference
		self.recent = time.monotonic()
		self._speed = 0.0 # float speed
		self.switch.when_pressed = self.closed_alert
		self.threshold = .4469 #.4469m/s = 1mph, below this readout we want 0
	
	@property
	def speed(self):
		now = time.monotonic()
		dt = now - self.recent
		dt_threshold = self.circumference/self.threshold
		if dt > dt_threshold:
			self._speed = 0.0 # if sensor hasn't triggered in a while
		return self._speed
	def closed_alert(self):
		now = time.monotonic()
		dt = now - self.recent
		dt_threshold = self.circumference/self.threshold
		self._speed = self.dist_per_dt/dt
		self.recent = now #back to next cycle


# The reedspeed_logger function continuously outputs an updated speed 
# scalar to the function that called it

instance = reedswitch(26, 2.096)
timestamp = time.strftime("%Y%m%d-%H%M%S")
folder = "reedspeed captures"
filename = f"reedspeed_log_{timestamp}.csv"
filepath = os.path.join(folder,filename)
file_exists = os.path.isfile(filepath)
print(f"Logging speed data to {filename}. Ctrl+C to stop.")


with open(filepath, mode='a', newline = '') as csvfile:
	fieldnames = ['time', 'speed']
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	
	# headers at top of csv:
	if not file_exists:
		writer.writeheader()
	try:
		while True:
			cur = datetime.datetime.now()
			t = time.strftime("%Y-%m-%d %H:%M:%S") + f".{cur.microsecond//1000:03d}"
			speed_now = instance.speed
			writer.writerow({
						'time': t,
						'speed': f"{speed_now:.2f}"
					})
			
			# following lines are strictly for demo'ing
			speedmph = speed_now/.4469
			
			formatted = f"{speedmph:.3f}"
			print(formatted)
			time.sleep(.5)
	except KeyboardInterrupt:
		exit()

	
