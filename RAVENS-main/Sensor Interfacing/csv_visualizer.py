# given a valid csv filepath and 2 fields of interest, plot a graph

import sys
import pandas as pd
import matplotlib.pyplot as plt

filename = sys.argv[1]
field1 = sys.argv[2]
field2 = sys.argv[3]

def csv_plot(filename, field1, field2):
	data = pd.read_csv(filename)
	data.plot(x=field1, y=field2)
	plt.show()

csv_plot(filename, field1, field2)
