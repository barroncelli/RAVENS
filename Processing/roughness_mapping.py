# the roughness_mapping program takes in a .csv file of timestamped
# IMU data and performs spectral processing to isolate road noise.

# The preliminary roughness reading is then normalized by the 
# bicycle speed. GPS mapping will be applied in post-processing.

# see the following for road roughness guidelines:
# iso.org/obp/ui/fr/#iso:std:iso:8608:ed-1:v1:en:sec:D

def roughness_mapping(imu_csv, speedcsv, gradecsv):
	import numpy as np
	import csv

	#visualization aid:
	import matplotlib.pyplot as plt
	
	#broad strokes: scrape timestamped speed, timestamped acceleration,
	# match accels to speeds by timestamp, normalize for gravity and
	# velocity in pre processing
	
	accels_z = 
	# should be in rads from horizontal:
	grades = 
	speeds = 
	
	# Intermediary, make sure that there are the same number
	# of entries in accels, grades, and speeds
	
	grav = -9.81*(np.cos(grades))
	gravcomped = accels_z + grav
	
	gamma = 1.5 # polynomial factor between speed and vertical 
	            # acceleration from vibrations, to
	            # be refined experimentally
	
	# RMS vibration intensity is proportional to speed^gamma
	speed_scaled = speeds ** gamma
	
	speedgrav_azs = gravcomped/speed_scaled
	
	# We will process road length in discrete blocks:
	# this could be done by declaring equal distances
	# per block, but our frequency resolution would then depend on
	# our speed. It is more consistent processing-wise to look
	# at blocks of fixed time and variable distance.
	
	blockperiod = 2 # achieves good frequency resolution
	# IMU sampling freq:
	fs = 
	
	samplesperblock = blockperiod/fs
	numsamples = speedgrav_azs.size()
	remainder = numsamples % samplesperblock
	
	if not remainder == 0: # only need to slice when a remainder exists
		speedgrav_azs = speedgrav_azs[:-remainder] 
		speeds = speeds[:-remainder] #we need to calc speed per block
	
	# azblocks has a block in each row
	azblocks = speedgrav_azs.reshape(-1, samplesperblock)
	
	
	window = np.hanning(samplesperblock) #get rid of discontinuities
	# apply to each row
	windowed = azblocks*window[np.newaxis, :]
	spectrum_azs = np.fft.rfft(windowed, axis=1)
	
	# could further manipulated spectrum to characterize
	# different types of road surface
	
	magnitudes = np.abs(spectrum_azs) ** 2
	# normalize b/c rfft takes half spectrum
	magnitudes[1:-1] *= 2 # exclude DC power at freq=0
	# Hann window scale factor = .375
	magnitudes *= 1/.375
	
	time_to_spatial = magnitudes/(fs * samplesperblock)
	
	# importantly: frequencies scale with velocity.
	# if I hit a bump every meter, this will be a 1 hz component at 1/ms
	# but 5 hz for 5 m/s
	
	# our imu data is time-indexed, not position-indexed, so:
	# fnormalized = f/speed
	
	# form the speed into blocks, 1 per row
	speedblocks = speeds.reshape(samplesperblock, -1)
	# we will approximate speed in each block as a constant for block duration
	speedavgs = np.mean(speedblocks, axis=1)
	
	# speed normalized spatial spectra:
	PSDs = time_to_spatial/speedavgs
	
	
	# We will eventually want a positional map rather than temporal
	
	

	
	
