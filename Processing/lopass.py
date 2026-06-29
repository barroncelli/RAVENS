import finufft
import numpy as np
import csv
import matplotlib.pyplot as plt
import pandas as pd

file = "/home/bcelli/Projects/RAVENS/Sensor Interfacing/full captures/qloop.csv"
data = pd.read_csv(file)

t = pd.to_datetime(data["timestamp"])

ax = data["accel_x"]
ay = data["accel_y"]
az = data["accel_z"]
speeds = data["speed"]

grades = 100*ay/az
