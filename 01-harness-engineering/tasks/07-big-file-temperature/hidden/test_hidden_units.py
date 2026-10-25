import pytest
import units

EXPECTED = [
    ('kilowatt_hours_to_calories', 860420.650096),
    ('grams_to_kilograms', 0.001),
    ('meters_to_inches', 39.3700787402),
    ('centimeters_to_kilometers', 1e-05),
    ('cups_to_milliliters', 236.5882365),
    ('pints_to_liters', 0.473176473),
    ('feet_to_centimeters', 30.48),
    ('megabytes_to_gigabytes', 0.001),
    ('seconds_to_weeks', 1.65343915344e-06),
    ('centimeters_to_miles', 6.21371192237e-06),
    ('ounces_to_kilograms', 0.028349523125),
    ('joules_to_kilowatt_hours', 2.77777777778e-07),
    ('calories_to_kilowatt_hours', 1.16222222222e-06),
    ('days_to_seconds', 86400.0),
    ('miles_to_kilometers', 1.609344),
    ('miles_per_hour_to_meters_per_second', 0.44704),
    ('cups_to_liters', 0.2365882365),
    ('kilobytes_to_kibibytes', 0.9765625),
    ('days_to_weeks', 0.142857142857),
    ('miles_to_centimeters', 160934.4),
    ('centimeters_to_millimeters', 10.0),
    ('gallons_to_liters', 3.785411784),
    ('kibibytes_to_kilobytes', 1.024),
    ('tonnes_to_ounces', 35273.9619496),
    ('weeks_to_hours', 168.0),
    ('weeks_to_days', 7.0),
    ('kibibytes_to_gigabytes', 1.024e-06),
    ('centimeters_to_inches', 0.393700787402),
    ('gigabytes_to_bytes', 1000000000.0),
    ('kilometers_to_feet', 3280.83989501),
    ('pounds_to_tonnes', 0.00045359237),
    ('tonnes_to_pounds', 2204.62262185),
    ('kilojoules_to_kilowatt_hours', 0.000277777777778),
    ('pascals_to_psi', 0.00014503773773),
    ('kilometers_to_centimeters', 100000.0),
    ('grams_to_ounces', 0.0352739619496),
    ('kilometers_per_hour_to_meters_per_second', 0.277777777778),
    ('meters_to_millimeters', 1000.0),
    ('knots_to_miles_per_hour', 1.15077845383),
    ('pounds_to_grams', 453.59237),
    ('centimeters_to_meters', 0.01),
    ('ounces_to_grams', 28.349523125),
    ('millimeters_to_miles', 6.21371192237e-07),
    ('kilopascals_to_psi', 0.14503773773),
    ('tonnes_to_kilograms', 1000.0),
    ('inches_to_feet', 0.0833333333333),
    ('pascals_to_bars', 1e-05),
    ('kilometers_per_hour_to_knots', 0.539957269941),
    ('liters_to_pints', 2.11337641887),
    ('calories_to_kilojoules', 0.004184),
    ('kilometers_per_hour_to_miles_per_hour', 0.621371192237),
    ('calories_to_joules', 4.184),
    ('kilopascals_to_bars', 0.01),
    ('feet_to_kilometers', 0.0003048),
    ('kilograms_to_grams', 1000.0),
    ('millimeters_to_feet', 0.00328083989501),
    ('kilojoules_to_joules', 1000.0),
    ('seconds_to_days', 1.15740740741e-05),
    ('meters_to_centimeters', 100.0),
    ('grams_to_pounds', 0.00220462262185),
]


@pytest.mark.parametrize("name,factor", EXPECTED)
def test_existing_conversions_untouched(name, factor):
    assert getattr(units, name)(3) == pytest.approx(3 * factor, rel=1e-9)


def test_every_conversion_still_exists():
    assert len(units.available_conversions()) >= 164


def test_temperature_values():
    assert units.kelvin_to_fahrenheit(373.15) == pytest.approx(212.0)
    assert units.fahrenheit_to_celsius(212) == pytest.approx(100.0)
    assert units.convert(-40, "celsius", "fahrenheit") == pytest.approx(-40.0)
    assert units.celsius_to_kelvin(-273.15) == pytest.approx(0.0)


@pytest.mark.parametrize("fn,value", [
    ("celsius_to_fahrenheit", -273.16), ("celsius_to_kelvin", -300),
    ("fahrenheit_to_celsius", -460), ("fahrenheit_to_kelvin", -500),
    ("kelvin_to_celsius", -0.01), ("kelvin_to_fahrenheit", -1),
])
def test_below_absolute_zero(fn, value):
    with pytest.raises(ValueError):
        getattr(units, fn)(value)
