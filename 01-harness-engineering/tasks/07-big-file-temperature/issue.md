Temperature conversions in `units.py` are wrong. `celsius_to_fahrenheit(100)` returns `203.0`; it should be `212.0`. Everything that goes through it (`kelvin_to_fahrenheit`, `convert(..., "celsius", "fahrenheit")`) is wrong too.

Also, all six temperature functions must raise `ValueError` when the input is below absolute zero (-273.15 °C, -459.67 °F, 0 K) instead of returning a number.

The other conversions in the file are correct and used everywhere; don't change them.
