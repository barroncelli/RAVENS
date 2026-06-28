
# Zero-order hold for real-time extrapolation
# this must be called every single sample for best realtime
# speed approximation


# time period between samples:
# this is dynamic for hall effect sensor, will need a way to indicate
# new measurement has been made and turn this into dt
dt = 

# this reading:
cur = 
prev = 

a_est = (cur-prev)/dt

# maybe use a datetime.now() type of call to get time elapsed
time_elapsed = 
speed_now = cur + a_est*time_elapsed

# output speed_now to function that called it

