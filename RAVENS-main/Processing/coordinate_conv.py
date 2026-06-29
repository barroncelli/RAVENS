# maps stationary bike IMU coordinates to new x,y,z coordinate system
# prints out a corresponding rotation matrix
#
# When finding the bike stationary coords, ensure you plumb the frame
# instead of trying to balance it because bikes are uneven
#
# The way I mounted it, y is longitudinal and x is transverse horizontal
# z is vertical
# do this with a rotation matrix

import numpy as np

# offsets

x_stationary = -0.36

y_stationary = 0.82

z_stationary = 9.67

g_stationary = [x_stationary, y_stationary, z_stationary]
mag = np.sqrt(x_stationary**2 + y_stationary**2 + z_stationary**2)

znew = g_stationary/mag # our desired z vector in current reference frame


# start with x because it's more independent from z than y is from z
x_ideal = np.array([1,0,0])
# find correlation to z desired and subtract from ideal x
xnew = x_ideal-np.dot(x_ideal, znew)*znew 
xnew = xnew/np.linalg.norm(xnew) #rescale

ynew = np.cross(znew, xnew)

# rotation matrix:
R = np.column_stack([xnew, ynew, znew])
print(R)
