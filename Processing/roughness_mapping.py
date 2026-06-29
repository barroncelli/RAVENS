# the roughness_mapping program takes in a .csv file of timestamped
# IMU data and performs spectral processing to isolate road noise.

# The preliminary roughness reading is then normalized by the 
# bicycle speed. GPS mapping will be applied in post-processing.

# see the following for road roughness guidelines:
# iso.org/obp/ui/fr/#iso:std:iso:8608:ed-1:v1:en:sec:D

#def roughness_mapping(imu_csv, speedcsv, gradecsv):

import numpy as np
import csv
import matplotlib.pyplot as plt
import pandas as pd

file = r"C:\Users\barro\Downloads\RAVENS-main\RAVENS-main\Sensor Interfacing\full captures\full_log_20260627-203114.csv"

gfile = r"C:\Users\barro\Downloads\RAVENS-main\RAVENS-main\Sensor Interfacing\full captures\cleaned_grades.csv"
gradef = pd.read_csv(gfile)
grades = gradef["Grade"]

data = pd.read_csv(file)
data = data[:135000]

t = pd.to_datetime(data["timestamp"])



#broad strokes: scrape timestamped speed, timestamped acceleration,
# match accels to speeds by timestamp, normalize for gravity and
# velocity in pre processing

accels_z = data["accel_z"]
#accels_z = accels_z.ffill().bfill() # get rid of missing entires
# should be in rads from horizontal:
grades = np.arctan(grades/100)
speeds = data["speed"]

# Intermediary, make sure that there are the same number
# of entries in accels, grades, and speeds

grav = -9.81*(np.cos(grades))
gravcomped = accels_z + grav

gamma = 1.5 # polynomial factor between speed and vertical 
            # acceleration from vibrations, to
            # be refined experimentally

# RMS vibration intensity is proportional to speed^gamma
speed_scaled = speeds ** gamma

speedgrav_azs = np.zeros(gravcomped.size)
np.divide(gravcomped, speed_scaled, out=speedgrav_azs, where=(speed_scaled!=0))

# We will process road length in discrete blocks:
# this could be done by declaring equal distances
# per block, but our frequency resolution would then depend on
# our speed. It is more consistent processing-wise to look
# at blocks of fixed time and variable distance.

blockperiod = 2 # achieves good frequency resolution
# IMU sampling freq:
fs = 100

samplesperblock = blockperiod*fs
numsamples = speedgrav_azs.size
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
f_time = np.fft.rfftfreq(samplesperblock, d=1/fs)
# could further manipulate spectrum to characterize
# different types of road surface

magnitudes = np.abs(spectrum_azs) ** 2
# normalize b/c rfft takes half spectrum:
magnitudes[1:-1] *= 2 # exclude DC power at freq=0
# Hann window scale factor = .375
magnitudes *= 1/.375

time_scaled = magnitudes/(fs * samplesperblock)

# importantly: frequencies scale with velocity.
# if I hit a bump every meter, this will be a 1 hz component at 1/ms
# but 5 hz for 5 m/s

# our imu data is time-indexed, not position-indexed, so:
# fnormalized = f/speed

# form the speed into blocks, 1 per row
speedblocks = speeds.values.reshape(-1, samplesperblock)
# we will approximate speed in each block as a constant for block duration
speedavgs = np.mean(speedblocks, axis=1)

plt.ioff()
plt.figure()

block_count = time_scaled.shape[0]

spatial_spectra = np.zeros_like(time_scaled)
for i in range(block_count): #loop over each block
        s = speedavgs[i]
        fspatial = np.zeros(f_time.size)
        np.divide(f_time, s, out=fspatial, where=(s!=0))
        spatial_spectra[i] = fspatial

        if i % 97 == 0:
                plt.plot(fspatial, time_scaled[i, :])

# if  using weird blocksizes then do remainder logic before this:
tnew = t[::samplesperblock]

# speed normalized spatial spectra magntitudes:
PSDs = np.zeros(block_count)
for block in range(block_count):
        psd = (1/(fs*samplesperblock)) * np.sum(spatial_spectra[block]) ** 2
        PSDs[block] = psd

#Outlier correction:
upper = 20
lower = 0 
invalidmask = (PSDs<lower)|(PSDs>upper)
PSDs[invalidmask] = np.nan

cleaned = pd.Series(PSDs).ffill().to_numpy()

plt.figure()
plt.plot(tnew, PSDs)
plt.show()


# We will eventually want a positional map rather than temporal



	
	
