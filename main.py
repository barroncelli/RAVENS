# calls on various RAVENS helper functions and outputs
# our aerodynamic drag

import numpy as np






# grade:
# blah blah blah UKF

trust = False
accel_current = (0,0,0) # this will be modified in following function
imu_threshold(csv, current_grade, trust, accel_current)

if trust == True:
	# we should update kalman model to reflect this
	ax = accel_current[0]
	az = accel_current[2]
	grade = np.atan(ax/az)
	# put this grade into KF









# wind:

#poll the wind sensor and put into something that the final CdA filter can use










# power:
# poll the powermeter over ANT+








# speed:
# interface hall effect sensor and decide whether to let each measurement
# be absolute truth or to smoothly curve between measurements (interpolate)




# CdA: 
# d/dt(momentum)= power + force of gravity + rolling resistance + air resistance
# + constant bike inefficiency (chain friction etc)




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
Fmech = .3*P/v + 3

# Drag force = 1/2 rho*cda*v^2
# air density rho:

#H = humidity from BME
#T = temp in celsius from BME
#P = pressure in pascals from BME

rho = (P-(H*610.78*np.exp((17.27*T)/(T+237.3)))/(287.058*(T+273.15)) + 
	(H*610.78*np.exp((17.27*T)/(T+237.3))/(461.5*(T+273.15)))

# Fdrag = .5*rho*cDa*v_wind^2

# m dv/dt = mgsin(theta) + P/v - Frolling - Fmech - Fdrag

#Fdrag = -8-.03*P/v - m dv/dt + mgsin(theta) + P/v
#Fdrag = .97*P/v - m dv/dt + mgsin(theta) - 8

#CdA = (2/(rho*v_wind^2)) * (.97*P/v - m dv/dt + mgsin(theta) - 8)
# Our unknowns: rho (needs temp, pressure, humidity), mass, power, 
# velocity, wind velocity, and theta (grade)
