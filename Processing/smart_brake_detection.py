# The smart_brake_detection program takes in a braking bool and 
# modifies it, if needed, to provide an update on the rider's
# current braking state.

# The program determines whether a cyclist is braking
# based on a combination of change in longitudinal acceleration and
# (to be implemented later), a rapid spike in (computed) CdA. 


def smart_brake_detection(braking, axlist, azlist, gradelist)
	import numpy as np
	
	# maybe a second or so of longitudinal acceleration to ax_list
	# this must be gravity-isolated to account for grade
	# simple enough: assume roll angle to be negligible, 
	# 
	
	
	#az_arr = np.array(az_list)
	#grav_compensator = np.arctan(ax_arr/az_arr)
	grade_arr = np.array(gradelist)
	ax_arr = np.array(axlist)
	# grade arrives in radians
	grav = -9.81*(np.sin(grade_arr))
	grav_comped_axs = grade_arr + grav
	
	
	last_ax = grav_comped_axs.size()

	# min m/s/s boundary to determine whether brakes have been applied
	thresh = 3 

	# CdA = ...
	
	# case to deal with pedaling again after braking
	if braking = True and grav_comped_axs[last_ax] > 0:
		# imprecise but predictable method to guarantee 
		# brakes have been released
		braking = False

	
	# now, check that new entry is < 0 and meets threshold
	if [grav_comped_axs[last_ax] < 0 and 
		grav_comped_axs[last_ax] < grav_comped_axs[0] - thresh]:
		braking = True


	
