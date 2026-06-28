# given a passed-in IMU csv dataset, the ferro_detector file
# generates a time plot of magnetic intensity. In the future, 
# it may be wise to normalize readings for the Earth's natural 
# magnetic field.

import numpy as np
import matplotlib.pyplot as plt
import csv

with open("bno captures/bno_log_20260619-170214.csv", "r") as f:
		logs = csv.reader(f)
		rows = list(logs)	
		time_arr = np.arange(len(rows))
		mtotal =  np.zeros(len(rows))

		for rowint in range(len(rows)-2): #skip first 2 rows, so our range is short
			row = rowint+2    #first line is titles, second is all zeroes
			
			#time_arr[row] = rows[row][0] # could be nice to fix this and 
				# map plot to actual timestamps
											
			mx = rows[row][7]
			my = rows[row][8]
			mz = rows[row][9]
			this_m = np.sqrt(float(mx)**2 + float(my)**2 + float(mz)**2)
			# handle saturation spikes that distort plot
			if this_m < 500:
				mtotal[row] = this_m
			else:
				mtotal[row] = mtotal[row-1]

		plt.plot(time_arr, mtotal)
		plt.show()
