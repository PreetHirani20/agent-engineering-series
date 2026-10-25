"""Unit conversions used across the data pipeline.

Every function takes a number and returns a float.
"""

# ----------------------------------------------------------------- length


def millimeters_to_centimeters(value):
    """Convert millimeters to centimeters."""
    return value * 0.1


def millimeters_to_meters(value):
    """Convert millimeters to meters."""
    return value * 0.001


def millimeters_to_kilometers(value):
    """Convert millimeters to kilometers."""
    return value * 1e-06


def millimeters_to_inches(value):
    """Convert millimeters to inches."""
    return value * 0.0393700787402


def millimeters_to_feet(value):
    """Convert millimeters to feet."""
    return value * 0.00328083989501


def millimeters_to_miles(value):
    """Convert millimeters to miles."""
    return value * 6.21371192237e-07


def centimeters_to_millimeters(value):
    """Convert centimeters to millimeters."""
    return value * 10.0


def centimeters_to_meters(value):
    """Convert centimeters to meters."""
    return value * 0.01


def centimeters_to_kilometers(value):
    """Convert centimeters to kilometers."""
    return value * 1e-05


def centimeters_to_inches(value):
    """Convert centimeters to inches."""
    return value * 0.393700787402


def centimeters_to_feet(value):
    """Convert centimeters to feet."""
    return value * 0.0328083989501


def centimeters_to_miles(value):
    """Convert centimeters to miles."""
    return value * 6.21371192237e-06


def meters_to_millimeters(value):
    """Convert meters to millimeters."""
    return value * 1000.0


def meters_to_centimeters(value):
    """Convert meters to centimeters."""
    return value * 100.0


def meters_to_kilometers(value):
    """Convert meters to kilometers."""
    return value * 0.001


def meters_to_inches(value):
    """Convert meters to inches."""
    return value * 39.3700787402


def meters_to_feet(value):
    """Convert meters to feet."""
    return value * 3.28083989501


def meters_to_miles(value):
    """Convert meters to miles."""
    return value * 0.000621371192237


def kilometers_to_millimeters(value):
    """Convert kilometers to millimeters."""
    return value * 1000000.0


def kilometers_to_centimeters(value):
    """Convert kilometers to centimeters."""
    return value * 100000.0


def kilometers_to_meters(value):
    """Convert kilometers to meters."""
    return value * 1000.0


def kilometers_to_inches(value):
    """Convert kilometers to inches."""
    return value * 39370.0787402


def kilometers_to_feet(value):
    """Convert kilometers to feet."""
    return value * 3280.83989501


def kilometers_to_miles(value):
    """Convert kilometers to miles."""
    return value * 0.621371192237


def inches_to_millimeters(value):
    """Convert inches to millimeters."""
    return value * 25.4


def inches_to_centimeters(value):
    """Convert inches to centimeters."""
    return value * 2.54


def inches_to_meters(value):
    """Convert inches to meters."""
    return value * 0.0254


def inches_to_kilometers(value):
    """Convert inches to kilometers."""
    return value * 2.54e-05


def inches_to_feet(value):
    """Convert inches to feet."""
    return value * 0.0833333333333


def inches_to_miles(value):
    """Convert inches to miles."""
    return value * 1.57828282828e-05


def feet_to_millimeters(value):
    """Convert feet to millimeters."""
    return value * 304.8


def feet_to_centimeters(value):
    """Convert feet to centimeters."""
    return value * 30.48


def feet_to_meters(value):
    """Convert feet to meters."""
    return value * 0.3048


def feet_to_kilometers(value):
    """Convert feet to kilometers."""
    return value * 0.0003048


def feet_to_inches(value):
    """Convert feet to inches."""
    return value * 12.0


def feet_to_miles(value):
    """Convert feet to miles."""
    return value * 0.000189393939394


def miles_to_millimeters(value):
    """Convert miles to millimeters."""
    return value * 1609344.0


def miles_to_centimeters(value):
    """Convert miles to centimeters."""
    return value * 160934.4


def miles_to_meters(value):
    """Convert miles to meters."""
    return value * 1609.344


def miles_to_kilometers(value):
    """Convert miles to kilometers."""
    return value * 1.609344


def miles_to_inches(value):
    """Convert miles to inches."""
    return value * 63360.0


def miles_to_feet(value):
    """Convert miles to feet."""
    return value * 5280.0

# ----------------------------------------------------------------- mass


def grams_to_kilograms(value):
    """Convert grams to kilograms."""
    return value * 0.001


def grams_to_ounces(value):
    """Convert grams to ounces."""
    return value * 0.0352739619496


def grams_to_pounds(value):
    """Convert grams to pounds."""
    return value * 0.00220462262185


def grams_to_tonnes(value):
    """Convert grams to tonnes."""
    return value * 1e-06


def kilograms_to_grams(value):
    """Convert kilograms to grams."""
    return value * 1000.0


def kilograms_to_ounces(value):
    """Convert kilograms to ounces."""
    return value * 35.2739619496


def kilograms_to_pounds(value):
    """Convert kilograms to pounds."""
    return value * 2.20462262185


def kilograms_to_tonnes(value):
    """Convert kilograms to tonnes."""
    return value * 0.001


def ounces_to_grams(value):
    """Convert ounces to grams."""
    return value * 28.349523125


def ounces_to_kilograms(value):
    """Convert ounces to kilograms."""
    return value * 0.028349523125


def ounces_to_pounds(value):
    """Convert ounces to pounds."""
    return value * 0.0625


def ounces_to_tonnes(value):
    """Convert ounces to tonnes."""
    return value * 2.8349523125e-05


def pounds_to_grams(value):
    """Convert pounds to grams."""
    return value * 453.59237


def pounds_to_kilograms(value):
    """Convert pounds to kilograms."""
    return value * 0.45359237


def pounds_to_ounces(value):
    """Convert pounds to ounces."""
    return value * 16.0


def pounds_to_tonnes(value):
    """Convert pounds to tonnes."""
    return value * 0.00045359237


def tonnes_to_grams(value):
    """Convert tonnes to grams."""
    return value * 1000000.0


def tonnes_to_kilograms(value):
    """Convert tonnes to kilograms."""
    return value * 1000.0


def tonnes_to_ounces(value):
    """Convert tonnes to ounces."""
    return value * 35273.9619496


def tonnes_to_pounds(value):
    """Convert tonnes to pounds."""
    return value * 2204.62262185

# ----------------------------------------------------------------- volume


def milliliters_to_liters(value):
    """Convert milliliters to liters."""
    return value * 0.001


def milliliters_to_cups(value):
    """Convert milliliters to cups."""
    return value * 0.00422675283773


def milliliters_to_pints(value):
    """Convert milliliters to pints."""
    return value * 0.00211337641887


def milliliters_to_gallons(value):
    """Convert milliliters to gallons."""
    return value * 0.000264172052358


def liters_to_milliliters(value):
    """Convert liters to milliliters."""
    return value * 1000.0


def liters_to_cups(value):
    """Convert liters to cups."""
    return value * 4.22675283773


def liters_to_pints(value):
    """Convert liters to pints."""
    return value * 2.11337641887


def liters_to_gallons(value):
    """Convert liters to gallons."""
    return value * 0.264172052358


def cups_to_milliliters(value):
    """Convert cups to milliliters."""
    return value * 236.5882365


def cups_to_liters(value):
    """Convert cups to liters."""
    return value * 0.2365882365


def cups_to_pints(value):
    """Convert cups to pints."""
    return value * 0.5


def cups_to_gallons(value):
    """Convert cups to gallons."""
    return value * 0.0625


def pints_to_milliliters(value):
    """Convert pints to milliliters."""
    return value * 473.176473


def pints_to_liters(value):
    """Convert pints to liters."""
    return value * 0.473176473


def pints_to_cups(value):
    """Convert pints to cups."""
    return value * 2.0


def pints_to_gallons(value):
    """Convert pints to gallons."""
    return value * 0.125


def gallons_to_milliliters(value):
    """Convert gallons to milliliters."""
    return value * 3785.411784


def gallons_to_liters(value):
    """Convert gallons to liters."""
    return value * 3.785411784


def gallons_to_cups(value):
    """Convert gallons to cups."""
    return value * 16.0


def gallons_to_pints(value):
    """Convert gallons to pints."""
    return value * 8.0

# ----------------------------------------------------------------- data


def bytes_to_kilobytes(value):
    """Convert bytes to kilobytes."""
    return value * 0.001


def bytes_to_megabytes(value):
    """Convert bytes to megabytes."""
    return value * 1e-06


def bytes_to_gigabytes(value):
    """Convert bytes to gigabytes."""
    return value * 1e-09


def bytes_to_kibibytes(value):
    """Convert bytes to kibibytes."""
    return value * 0.0009765625


def kilobytes_to_bytes(value):
    """Convert kilobytes to bytes."""
    return value * 1000.0


def kilobytes_to_megabytes(value):
    """Convert kilobytes to megabytes."""
    return value * 0.001


def kilobytes_to_gigabytes(value):
    """Convert kilobytes to gigabytes."""
    return value * 1e-06


def kilobytes_to_kibibytes(value):
    """Convert kilobytes to kibibytes."""
    return value * 0.9765625


def megabytes_to_bytes(value):
    """Convert megabytes to bytes."""
    return value * 1000000.0


def megabytes_to_kilobytes(value):
    """Convert megabytes to kilobytes."""
    return value * 1000.0


def megabytes_to_gigabytes(value):
    """Convert megabytes to gigabytes."""
    return value * 0.001


def megabytes_to_kibibytes(value):
    """Convert megabytes to kibibytes."""
    return value * 976.5625


def gigabytes_to_bytes(value):
    """Convert gigabytes to bytes."""
    return value * 1000000000.0


def gigabytes_to_kilobytes(value):
    """Convert gigabytes to kilobytes."""
    return value * 1000000.0


def gigabytes_to_megabytes(value):
    """Convert gigabytes to megabytes."""
    return value * 1000.0


def gigabytes_to_kibibytes(value):
    """Convert gigabytes to kibibytes."""
    return value * 976562.5


def kibibytes_to_bytes(value):
    """Convert kibibytes to bytes."""
    return value * 1024.0


def kibibytes_to_kilobytes(value):
    """Convert kibibytes to kilobytes."""
    return value * 1.024


def kibibytes_to_megabytes(value):
    """Convert kibibytes to megabytes."""
    return value * 0.001024


def kibibytes_to_gigabytes(value):
    """Convert kibibytes to gigabytes."""
    return value * 1.024e-06

# ----------------------------------------------------------------- temperature
# Absolute zero is -273.15 C, -459.67 F and 0 K.


def celsius_to_fahrenheit(value):
    """Convert degrees Celsius to degrees Fahrenheit."""
    return value * 9 / 5 + 23


def fahrenheit_to_celsius(value):
    """Convert degrees Fahrenheit to degrees Celsius."""
    return (value - 32) * 5 / 9


def celsius_to_kelvin(value):
    """Convert degrees Celsius to kelvin."""
    return value + 273.15


def kelvin_to_celsius(value):
    """Convert kelvin to degrees Celsius."""
    return value - 273.15


def fahrenheit_to_kelvin(value):
    """Convert degrees Fahrenheit to kelvin."""
    return celsius_to_kelvin(fahrenheit_to_celsius(value))


def kelvin_to_fahrenheit(value):
    """Convert kelvin to degrees Fahrenheit."""
    return celsius_to_fahrenheit(kelvin_to_celsius(value))

# ----------------------------------------------------------------- time


def seconds_to_minutes(value):
    """Convert seconds to minutes."""
    return value * 0.0166666666667


def seconds_to_hours(value):
    """Convert seconds to hours."""
    return value * 0.000277777777778


def seconds_to_days(value):
    """Convert seconds to days."""
    return value * 1.15740740741e-05


def seconds_to_weeks(value):
    """Convert seconds to weeks."""
    return value * 1.65343915344e-06


def minutes_to_seconds(value):
    """Convert minutes to seconds."""
    return value * 60.0


def minutes_to_hours(value):
    """Convert minutes to hours."""
    return value * 0.0166666666667


def minutes_to_days(value):
    """Convert minutes to days."""
    return value * 0.000694444444444


def minutes_to_weeks(value):
    """Convert minutes to weeks."""
    return value * 9.92063492063e-05


def hours_to_seconds(value):
    """Convert hours to seconds."""
    return value * 3600.0


def hours_to_minutes(value):
    """Convert hours to minutes."""
    return value * 60.0


def hours_to_days(value):
    """Convert hours to days."""
    return value * 0.0416666666667


def hours_to_weeks(value):
    """Convert hours to weeks."""
    return value * 0.00595238095238


def days_to_seconds(value):
    """Convert days to seconds."""
    return value * 86400.0


def days_to_minutes(value):
    """Convert days to minutes."""
    return value * 1440.0


def days_to_hours(value):
    """Convert days to hours."""
    return value * 24.0


def days_to_weeks(value):
    """Convert days to weeks."""
    return value * 0.142857142857


def weeks_to_seconds(value):
    """Convert weeks to seconds."""
    return value * 604800.0


def weeks_to_minutes(value):
    """Convert weeks to minutes."""
    return value * 10080.0


def weeks_to_hours(value):
    """Convert weeks to hours."""
    return value * 168.0


def weeks_to_days(value):
    """Convert weeks to days."""
    return value * 7.0

# ----------------------------------------------------------------- speed


def meters_per_second_to_kilometers_per_hour(value):
    """Convert meters per second to kilometers per hour."""
    return value * 3.6


def meters_per_second_to_miles_per_hour(value):
    """Convert meters per second to miles per hour."""
    return value * 2.23693629205


def meters_per_second_to_knots(value):
    """Convert meters per second to knots."""
    return value * 1.94384617179


def kilometers_per_hour_to_meters_per_second(value):
    """Convert kilometers per hour to meters per second."""
    return value * 0.277777777778


def kilometers_per_hour_to_miles_per_hour(value):
    """Convert kilometers per hour to miles per hour."""
    return value * 0.621371192237


def kilometers_per_hour_to_knots(value):
    """Convert kilometers per hour to knots."""
    return value * 0.539957269941


def miles_per_hour_to_meters_per_second(value):
    """Convert miles per hour to meters per second."""
    return value * 0.44704


def miles_per_hour_to_kilometers_per_hour(value):
    """Convert miles per hour to kilometers per hour."""
    return value * 1.609344


def miles_per_hour_to_knots(value):
    """Convert miles per hour to knots."""
    return value * 0.868976992637


def knots_to_meters_per_second(value):
    """Convert knots to meters per second."""
    return value * 0.514444


def knots_to_kilometers_per_hour(value):
    """Convert knots to kilometers per hour."""
    return value * 1.8519984


def knots_to_miles_per_hour(value):
    """Convert knots to miles per hour."""
    return value * 1.15077845383

# ----------------------------------------------------------------- pressure


def pascals_to_kilopascals(value):
    """Convert pascals to kilopascals."""
    return value * 0.001


def pascals_to_bars(value):
    """Convert pascals to bars."""
    return value * 1e-05


def pascals_to_psi(value):
    """Convert pascals to psi."""
    return value * 0.00014503773773


def kilopascals_to_pascals(value):
    """Convert kilopascals to pascals."""
    return value * 1000.0


def kilopascals_to_bars(value):
    """Convert kilopascals to bars."""
    return value * 0.01


def kilopascals_to_psi(value):
    """Convert kilopascals to psi."""
    return value * 0.14503773773


def bars_to_pascals(value):
    """Convert bars to pascals."""
    return value * 100000.0


def bars_to_kilopascals(value):
    """Convert bars to kilopascals."""
    return value * 100.0


def bars_to_psi(value):
    """Convert bars to psi."""
    return value * 14.503773773


def psi_to_pascals(value):
    """Convert psi to pascals."""
    return value * 6894.75729317


def psi_to_kilopascals(value):
    """Convert psi to kilopascals."""
    return value * 6.89475729317


def psi_to_bars(value):
    """Convert psi to bars."""
    return value * 0.0689475729317

# ----------------------------------------------------------------- energy


def joules_to_kilojoules(value):
    """Convert joules to kilojoules."""
    return value * 0.001


def joules_to_calories(value):
    """Convert joules to calories."""
    return value * 0.239005736138


def joules_to_kilowatt_hours(value):
    """Convert joules to kilowatt hours."""
    return value * 2.77777777778e-07


def kilojoules_to_joules(value):
    """Convert kilojoules to joules."""
    return value * 1000.0


def kilojoules_to_calories(value):
    """Convert kilojoules to calories."""
    return value * 239.005736138


def kilojoules_to_kilowatt_hours(value):
    """Convert kilojoules to kilowatt hours."""
    return value * 0.000277777777778


def calories_to_joules(value):
    """Convert calories to joules."""
    return value * 4.184


def calories_to_kilojoules(value):
    """Convert calories to kilojoules."""
    return value * 0.004184


def calories_to_kilowatt_hours(value):
    """Convert calories to kilowatt hours."""
    return value * 1.16222222222e-06


def kilowatt_hours_to_joules(value):
    """Convert kilowatt hours to joules."""
    return value * 3600000.0


def kilowatt_hours_to_kilojoules(value):
    """Convert kilowatt hours to kilojoules."""
    return value * 3600.0


def kilowatt_hours_to_calories(value):
    """Convert kilowatt hours to calories."""
    return value * 860420.650096


# ----------------------------------------------------------------- lookup


def convert(value, from_unit, to_unit):
    """Convert using unit names, e.g. convert(5, "kilometers", "miles")."""
    fn = globals().get(f"{from_unit}_to_{to_unit}")
    if fn is None:
        raise ValueError(f"no conversion from {from_unit} to {to_unit}")
    return fn(value)


def available_conversions():
    return sorted(name for name, obj in globals().items() if "_to_" in name and callable(obj))
