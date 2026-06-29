#  Estimate CDA Prototype

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import csv
from scipy.ndimage import uniform_filter1d


file = r"C:\Users\barro\Downloads\RAVENS-main\RAVENS-main\Sensor Interfacing\full captures\full_log_20260627-203114.csv"

data = pd.read_csv(file)
data = data[:135000]

t = pd.to_datetime(data["timestamp"])
speed = data["speed"]
power = data["power"]
windspeed = data["v_wind_est"]

mass = 110 #kg, approx

gfile = r"C:\Users\barro\Downloads\RAVENS-main\RAVENS-main\Sensor Interfacing\full captures\cleaned_grades.csv"
gradef = pd.read_csv(gfile)
grades = gradef["Grade"]
# should be in rads from horizontal:
grades = np.arctan(grades/100)

rho = 1.13 # approximate for today


# general eqns:
# force of gravity: fg = m*sin(theta)*-9.81, theta=grade

# momentum: p=mv, dp/dt = ma


# P = F_push*v
# F_push = P/v

# gatorskin tires in lab: at 18mph, 80psi,95 lb load for one tire: 22 watts
# Total setup for my bike is 110kg, higher psi so roughly the same per tire
# Approximately 40 watts combined
# 18mph = 5m/s
# F = P/v, F_tire = 40/5 = 8N

# Fchain&derailleur ~= 3% of input power
# non drivetrain mechanical losses (bearings) are about -3 watts
#Fmech = .3*P/v + 3

# Drag force = 1/2 rho*cda*v^2
# air density rho:

#H = humidity from BME
#T = temp in celsius from BME
#P = pressure in pascals from BME

#rho = (P-(H*610.78*np.exp((17.27*T)/(T+237.3)))/(287.058*(T+273.15)) + 
	#(H*610.78*np.exp((17.27*T)/(T+237.3))/(461.5*(T+273.15)))

# Fdrag = .5*rho*cDa*v_wind^2

# m dv/dt = mgsin(theta) + P/v - Frolling - Fmech - Fdrag

#Fdrag = -8-.03*P/v - m dv/dt + mgsin(theta) + P/v
#Fdrag = .97*P/v - m dv/dt + mgsin(theta) - 8

#CdA = (2/(rho*v_wind^2)) * (.97*P/v - m dv/dt + mgsin(theta) - 8)
# Our unknowns: rho (needs temp, pressure, humidity), mass, power, 
# velocity, wind velocity, and theta (grade)

blockperiod = 2 # reasonable length for cda
# data logging freq:
fs = 100
samplesperblock = blockperiod*fs

sblocks = speed.values.reshape(-1, samplesperblock)
smeans = np.mean(sblocks, axis=1)
# for speed < 3 m/s CdA is not meaningful, set to 0 (?)
smeans_clean = np.where(smeans<3, np.nan, smeans)
dv = np.diff(smeans)
# np.diff shortens arr by 1
dvdt = dv/blockperiod
dvdt = np.insert(dvdt, 0,0)
gblocks = grades.values.reshape(-1, samplesperblock)
gmeans = np.mean(gblocks, axis=1)
wblocks = windspeed.values.reshape(-1, samplesperblock)
wmeans = np.mean(wblocks, axis=1)
pblocks = power.values.reshape(-1, samplesperblock)
pmeans = np.mean(pblocks, axis=1)

tnew = t[::samplesperblock]


CdAs = (2/(rho*wmeans**2))*(.97*pmeans/smeans_clean-mass*dvdt+mass*-9.81*np.sin(gmeans)-8)

#Outlier correction:
upper = 10
lower = 0 
invalidmask = (CdAs<lower)|(CdAs>upper)
CdAs[invalidmask] = np.nan

cleaned = pd.Series(CdAs).ffill().bfill().to_numpy()
cdasmooth = uniform_filter1d(cleaned, size=10)
# convert back to pd:
#cdasmooth = pd.Series(cdasmooth, index=tnew)
#print(len(tnew), len(CdAs))
plt.figure()
plt.plot(tnew, cdasmooth)
plt.show()
