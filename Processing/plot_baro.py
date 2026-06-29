# plot elevation over a ride from baro data

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.ndimage import uniform_filter1d



file = r"C:\Users\barro\Downloads\RAVENS-main\RAVENS-main\Sensor Interfacing\full captures\full_log_20260627-203114.csv"

data = pd.read_csv(file)
data = data[:135000]

t = pd.to_datetime(data["timestamp"])
t_orig = t
p = data["pressure_bag"]
speed = data["speed"]

plt.figure()
plt.scatter(t, p, s=.1)

## plot the avgs

blockperiod = 2
fs = 100

samplesperblock = int(blockperiod*fs)
numsamples = p.size
remainder = numsamples % samplesperblock
	
if not remainder == 0: # only need to slice when a remainder exists
	p = p[:-remainder]
	t = t[:-remainder]
	speed = speed[:-remainder]
	
sblocks = speed.values.reshape(-1, samplesperblock)
dists = np.sum(sblocks, axis=1)
dists = dists/fs # normalize total meters per block
# would divide by blockperiod to get mean speed in m/s

psmooth = uniform_filter1d(p.values, size=samplesperblock)
dpsmooth = np.gradient(psmooth)
#dpblocks = dpsmooth.reshape(-1, samplesperblock)
pblocks = p.values.reshape(-1, samplesperblock)
mean_ps = np.mean(pblocks, axis=1)
dps = np.diff(mean_ps) # shortened length by 1
dps = np.insert(dps,0,0)

tnew = t[::samplesperblock]

dhs = 100*dps/(1.11*-9.81) # hpa to pa


dhdxs = np.zeros(dists.size)
np.divide(dhs, dists, out=dhdxs, where=(dists!=0))
dhdxs *= 100 # convert to pct

upper = 20
lower = -20 #technically some roads are steeper than this
invalidmask = (dhdxs<lower)|(dhdxs>upper)
dhdxs[invalidmask] = np.nan

cleaned = pd.Series(dhdxs).ffill().to_numpy() #fill outliers with prev val


filledclean = np.repeat(cleaned, samplesperblock)
filepath = r'C:\Users\barro\Downloads\RAVENS-main\RAVENS-main\Sensor Interfacing\full captures\cleaned_grades.csv'
df = pd.DataFrame({
    'Timestamp': t_orig,
    'Grade': filledclean
})

df.to_csv(filepath, index=False)

plt.figure()
plt.plot(tnew,mean_ps)
plt.ylabel("Mean Pressure")

plt.figure()
plt.plot(tnew, dhs, color='black')
plt.ylabel("Change in height (m)")

plt.figure()
plt.plot(tnew, cleaned, color='orange')
plt.ylabel("Percent Grade")
plt.ylim(-20,20)

plt.figure()
plt.plot(tnew, dists, color='green')
plt.ylabel("dist per block (m)")
plt.show()
