import time
import board
import busio
import adafruit_bme680

i2c = busio.I2C(board.SCL, board.SDA)
bme = adafruit_bme680.Adafruit_BME680_I2C(i2c, address=0x77)

print("adafruit_bme680 module:", adafruit_bme680.__file__)
print("BME object type:", type(bme))

# Show what attributes/methods exist (especially gas + oversampling related)
keys = [k for k in dir(bme) if any(s in k.lower() for s in ["gas","heater","oversample","filter","mode","wait","profile"])]
print("interesting attrs:", keys)

# Try the most common gas-disable knobs across versions
candidates = [
    ("gas_status", False),
    ("enable_gas", False),
    ("run_gas", False),
    ("_run_gas", False),
    ("heater_profile", 0),
    ("gas_heater_profile", 0),
]
for name, val in candidates:
    if hasattr(bme, name):
        try:
            setattr(bme, name, val)
            print(f"set {name}={val} (ok)")
        except Exception as e:
            print(f"set {name} failed:", name, repr(e))
    else:
        print(f"{name} not present")

# Ensure we set the *correct* oversample attribute names for your version
for name, val in [
    ("pressure_oversample", 1),
    ("temperature_oversample", 1),
    ("humidity_oversample", 1),
    ("filter_size", 0),
]:
    if hasattr(bme, name):
        try:
            setattr(bme, name, val)
            print(f"set {name}={val} (ok)")
        except Exception as e:
            print(f"set {name} failed:", name, repr(e))
    else:
        print(f"{name} not present")

# Time reads
for k in range(10):
    t0 = time.perf_counter()
    p = bme.pressure
    t1 = time.perf_counter()
    print(f"{k}: read_ms={(t1-t0)*1000:.1f}, p={p:.2f} hPa")
    time.sleep(0.1)
