import pandas as pd
import matplotlib.pyplot as plt

file = "/home/bcelli/Projects/RAVENS/Data Storage/mpl captures/mpl_log_20260620-084723.csv"

data = pd.read_csv(file)

t = pd.to_datetime(data["timestamp"])

plt.figure(figsize=(10,4))
plt.plot(t, data["altitude_m"])

plt.xlabel("Time")
plt.ylabel("Altitude (m)")
plt.show()
