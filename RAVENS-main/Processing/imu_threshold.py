# This program uses hard constraints for acceleration, magnitude, and calculated
# grade to determine whether a current situation is a high-confidence scenario
# that would allow us to calibrate our actual grade to an absolute setpoint
# from accelerometer data, rather than integrating and dead-reckoning with
# gyro rad/sec data.

# It takes two inputs, an input .csv file and a float corresponding to
# the grade computed by the Kalman filter, and outputs a trust bool
# and an accel_now tuple with ax,ay,az.

# We may want to update this in the future for time and cpu sake 
# to take in a curtailed .csv limited only to the number of samples
# we want to check, and have fixed indices for ax,ay,and az rather than
# finding them within this function with the .index() operator

def imu_threshold(inputcsv, UKFgrade, trust, accel_now):

	import numpy as np
	import csv


	# guilty until proven innocent: we default to distrusting data
	trust = False
	current_accels = (0,0,0)

	# acceleration magnitude deviation tolerance (units m/s/s):

	# this represents the deviation from gravity that we are willing to
	# accept. Our goal here is to determine when the bike is in an intertial
	# reference frame and use the relationship between ax (longitudinal)
	# and az (azimuthal) accelerations when gravity dominates the acceleration
	# profile to ground the UKF grade estimate, since gyro is prone to drift.

	atol = 0.2

	# number of samples over which we wish to verify that our accelerometer
	# readings have satisfied our constraints. Too high and we will never be able
	# to correct gyro drift, but if too low, little anomalies could infiltrate

	samples = 10

	# grade deviation tolerance (units in deg for now):

	# This is an outlier filtering mechanism more so than another precondition
	# to establish accelerometer trustworthiness. Essentially, we want to
	# ensure that our computed grade is not wildly off from our UKF
	# grade estimate
	gtol = 10

	# must feed in UKF grade and convert to deg
	grade = UKFgrade

	# must feed in ax,ay,az as real-time from BNO055 lib OR from csv file.
	# In broad strokes, we want to verify that the magnitude deviation has been
	# sub-threshold for some time

	#logistically, the simplest way to manage this seems to use .csv rows
	# to index each sample.

	#first, ensure that we are not at VERY beginning of the datastream, since
	# we want "samples" # of samples for confidence sake

	csv = []

	with open(inputcsv, 'r') as file:
		csv += list(csv.reader(file))

	head = csv[0]
	axindex = head.index('accel_x')
	ayindex = head.index('accel_y')
	azindex = head.index('accel_z')

	csv = csv[2:] #first line is header, second is all zeroes in my experience

	#FIND THE PASSED-IN ROW! CAN USE sys.argv or the like
	# In this testing stage, I will just use the last row as r
	r = csv.size() - 1 


	if r < samples: #can also update this to have a more aggressive threshold, like
	# r < samples * 10 or something because the first few seconds of data are not
	# trusty
		exit() # pick off early samples


	for index in range(samples):
		thisrow = r - samples + index + 1

		ax = csv[thisrow][axindex]
		ay = csv[thisrow][ayindex]
		az = csv[thisrow][azindex]
		#csv formats as str
		ax = float(ax)
		ay = float(ay)
		az = float(az)

		accel_mag = np.sqrt(ax**2 + ay**2 + az**2)

		if np.abs(accel_mag - 9.81) > atol: # fails our tolerance parameter
		# instantly pickoff these entries
			exit()
		# else, we can continue iterating

		# When we have satisfied acceleration magnitude parameter 
		# for desired # of samples, get current accelerations for final step
		if index == r-1:
			current_accels = (ax,ay,az)

	# now, filter outliers and ensure x & z adhere to grade estimate

	ax = current_accels[0]
	az = current_accels[2]
	pitch_measured = np.arctan(ax/az) # draw a picture to verify this
	pitch_measured = (180/np.pi)*pitch_measured # conv to degrees

	#could have done the grade outlier filter for all of samples within the above
	# for loop, but didn't want to worry about the dynamic grade over samples
	if np.abs(pitch_measured - grade) > gtol :
		# outlier
		exit()

	# NOW WE HAVE FAITH
	trust = True
