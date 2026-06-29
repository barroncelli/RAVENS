import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

file = r"C:\Users\barro\Downloads\RAVENS-main\RAVENS-main\Sensor Interfacing\full captures\full_log_20260627-203114.csv"

data = pd.read_csv(file)
data = data[:135000]

t = pd.to_datetime(data["timestamp"])

s = t.size
print(s)

ax = data["accel_x"]
ay = data["accel_y"]
az = data["accel_z"]

amag = np.sqrt(ax**2+ay**2+az**2)

# number of consecutive points desired
consec = 10
# bounds
margin = .7
center = 9.71
lowerbound = center-margin
upperbound = center+margin

# grade deviance for a single timestep
grade_dev = 5


inrange = (amag >= lowerbound) & (amag <= upperbound) # bool array
valid = np.zeros(len(amag), dtype=bool) # mask for all inrange points


count = 0
for i in range(len(inrange)):
	if inrange[i]: # checks whether is True
		count +=1
	else:
		if count >= consec:
			valid[i-count:i] = True
		count = 0

grades = np.zeros(len(amag))
for i in range(len(valid)):
	if valid[i]:
		ayhere = ay[i]
		azhere = az[i]
		grade = 100*ayhere/azhere # % GRADE NOT ANGLE
		grades[i] = grade
		
#count2 = 0
#for i in range(len(grades)-1):

plt.figure(figsize=(12, 8))
plt.subplot(2,1,1)
plt.scatter(t, amag, s=.1, color='black')
plt.scatter(t[valid], amag[valid], s=.5, color='green')
plt.ylim(9,10.5)
# resting gravity as computed by bno055 = 9.71 m/s/s
plt.axhline(y=lowerbound, color='red',linestyle="-")
plt.axhline(y=upperbound, color='red',linestyle="-")
plt.xlabel("Time")
plt.ylabel("Acceleration magnitude (m/s/s)")

plt.subplot(2,1,2)
plt.scatter(t[valid], grades[valid], s=.1)
plt.xlabel("Time")
plt.ylabel("Road percent grade")
plt.ylim(-10,10)
plt.tight_layout()

plt.figure()
plt.scatter(t, ay, s=.1, color='black')
plt.scatter(t, az, s=.1)

plt.figure()
plt.scatter(t, ax, s=.1, color='green')
plt.show()




binperiod = 2
fs = 100

samplesperblock = blockperiod*fs
numsamples = speedgrav_azs.size
remainder = numsamples % samplesperblock
	
if not remainder == 0: # only need to slice when a remainder exists
	speedgrav_azs = speedgrav_azs[:-remainder] 
	speeds = speeds[:-remainder]
	#we need to calc speed per block
	
# azblocks has a block in each row
azblocks = speedgrav_azs.reshape(-1, samplesperblock)




