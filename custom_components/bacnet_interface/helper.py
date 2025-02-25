"""Helper functions for the integration"""

from collections.abc import Mapping
from enum import StrEnum
import math
from typing import Collection

from homeassistant.components.sensor import SensorDeviceClass

from homeassistant.const import (
    UnitOfArea,
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    CONCENTRATION_MILLIGRAMS_PER_CUBIC_METER,
    CONCENTRATION_PARTS_PER_BILLION,
    CONCENTRATION_PARTS_PER_MILLION,
    DEGREE,
    LIGHT_LUX,
    PERCENTAGE,
    UnitOfReactivePower,
    REVOLUTIONS_PER_MINUTE,
    UnitOfApparentPower,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfIrradiance,
    UnitOfLength,
    UnitOfMass,
    UnitOfPower,
    UnitOfPrecipitationDepth,
    UnitOfPressure,
    UnitOfSoundPressure,
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolume,
    UnitOfVolumeFlowRate,
)


def key_to_property(key: str | None) -> str | None:
    match key:
        case "present_value" | "presentValue":
            return "presentValue"
        case "relinquish_default" | "relinquishDefault":
            return "relinquishDefault"
        case _:
            return None


def bacnet_to_ha_units(unit_in: str | None) -> str | None:
    match unit_in:
        case "amperes":
            return UnitOfElectricCurrent.AMPERE
        case "ampereSeconds":
            return None
        case "amperesPerMeter":
            return None
        case "amperesPerSquareMeter":
            return None
        case "ampereSquareHours":
            return None
        case "ampereSquareMeters":
            return None
        case "bars":
            return None
        case "becquerels":
            return None
        case "btus":
            return None
        case "btusPerHour":
            return UnitOfPower.BTU_PER_HOUR
        case "btusPerPound":
            return None
        case "btusPerPoundDryAir":
            return None
        case "candelas":
            return None
        case "candelasPerSquareMeter":
            return None
        case "centimeters":
            return UnitOfLength.CENTIMETERS
        case "centimetersOfMercury":
            return None
        case "centimetersOfWater":
            return UnitOfPrecipitationDepth.CENTIMETERS
        case "cubicFeet":
            return UnitOfVolume.CUBIC_FEET
        case "cubicFeetPerDay":
            return None
        case "cubicFeetPerHour":
            return None
        case "cubicFeetPerMinute":
            return UnitOfVolumeFlowRate.CUBIC_FEET_PER_MINUTE
        case "cubicFeetPerSecond":
            return None
        case "cubicMeters":
            return UnitOfVolume.CUBIC_METERS
        case "cubicMetersPerDay":
            return None
        case "cubicMetersPerHour":
            return UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR
        case "cubicMetersPerMinute":
            return None
        case "cubicMetersPerSecond":
            return None
        case "currency10":
            return None
        case "currency1":
            return None
        case "currency2":
            return None
        case "currency3":
            return None
        case "currency4":
            return None
        case "currency5":
            return None
        case "currency6":
            return None
        case "currency7":
            return None
        case "currency8":
            return None
        case "currency9":
            return None
        case "cyclesPerHour":
            return None
        case "cyclesPerMinute":
            return None
        case "days":
            return UnitOfTime.DAYS
        case "decibels":
            return UnitOfSoundPressure.DECIBEL
        case "decibelsA":
            return UnitOfSoundPressure.WEIGHTED_DECIBEL_A
        case "decibelsMillivolt":
            return None
        case "decibelsVolt":
            return None
        case "degreeDaysCelsius":
            return None
        case "degreeDaysFahrenheit":
            return None
        case "degreesAngular":
            return DEGREE
        case "degreesCelsius":
            return UnitOfTemperature.CELSIUS
        case "degreesCelsiusPerHour":
            return None
        case "degreesCelsiusPerMinute":
            return None
        case "degreesFahrenheit":
            return UnitOfTemperature.FAHRENHEIT
        case "degreesFahrenheitPerHour":
            return None
        case "degreesFahrenheitPerMinute":
            return None
        case "degreesKelvin":
            return UnitOfTemperature.KELVIN
        case "degreesKelvinPerHour":
            return None
        case "degreesKelvinPerMinute":
            return None
        case "degreesPhase":
            return DEGREE
        case "deltaDegreesFahrenheit":
            return None
        case "deltaDegreesKelvin":
            return None
        case "farads":
            return None
        case "feet":
            return UnitOfLength.FEET
        case "feetPerMinute":
            return None
        case "feetPerSecond":
            return UnitOfSpeed.FEET_PER_SECOND
        case "footCandles":
            return None
        case "grams":
            return UnitOfMass.GRAMS
        case "gramsOfWaterPerKilogramDryAir":
            return None
        case "gramsPerCubicCentimeter":
            return None
        case "gramsPerCubicMeter":
            return None
        case "gramsPerGram":
            return None
        case "gramsPerKilogram":
            return None
        case "gramsPerLiter":
            return None
        case "gramsPerMilliliter":
            return None
        case "gramsPerMinute":
            return None
        case "gramsPerSecond":
            return None
        case "gramsPerSquareMeter":
            return None
        case "gray":
            return None
        case "hectopascals":
            return UnitOfPressure.HPA
        case "henrys":
            return None
        case "hertz":
            return UnitOfFrequency.HERTZ
        case "horsepower":
            return None
        case "hours":
            return UnitOfTime.HOURS
        case "hundredthsSeconds":
            return None
        case "imperialGallons":
            return None
        case "imperialGallonsPerMinute":
            return None
        case "inches":
            return UnitOfLength.INCHES
        case "inchesOfMercury":
            return None
        case "inchesOfWater":
            return UnitOfPrecipitationDepth.INCHES
        case "joules":
            return None
        case "jouleSeconds":
            return None
        case "joulesPerCubicMeter":
            return None
        case "joulesPerDegreeKelvin":
            return None
        case "joulesPerHours":
            return None
        case "joulesPerKilogramDegreeKelvin":
            return None
        case "joulesPerKilogramDryAir":
            return None
        case "kilobecquerels":
            return None
        case "kiloBtus":
            return None
        case "kiloBtusPerHour":
            return None
        case "kilograms":
            return UnitOfMass.KILOGRAMS
        case "kilogramsPerCubicMeter":
            return None
        case "kilogramsPerHour":
            return None
        case "kilogramsPerKilogram":
            return None
        case "kilogramsPerMinute":
            return None
        case "kilogramsPerSecond":
            return None
        case "kilohertz":
            return UnitOfFrequency.KILOHERTZ
        case "kilohms":
            return None
        case "kilojoules":
            return None
        case "kilojoulesPerDegreeKelvin":
            return None
        case "kilojoulesPerKilogram":
            return None
        case "kilojoulesPerKilogramDryAir":
            return None
        case "kilometers":
            return UnitOfLength.KILOMETERS
        case "kilometersPerHour":
            return UnitOfSpeed.KILOMETERS_PER_HOUR
        case "kilopascals":
            return UnitOfPressure.KPA
        case "kilovoltAmpereHours":
            return None
        case "kilovoltAmpereHoursReactive":
            return None
        case "kilovoltAmperes":
            return UnitOfApparentPower.VOLT_AMPERE
        case "kilovoltAmperesReactive":
            return None
        case "kilovolts":
            return None
        case "kilowattHours":
            return UnitOfEnergy.KILO_WATT_HOUR
        case "kilowattHoursPerSquareFoot":
            return None
        case "kilowattHoursPerSquareMeter":
            return None
        case "kilowattHoursReactive":
            return None
        case "kilowatts":
            return UnitOfPower.KILO_WATT
        case "liters":
            return UnitOfVolume.LITERS
        case "litersPerHour":
            return None
        case "litersPerMinute":
            return UnitOfVolumeFlowRate.LITERS_PER_MINUTE
        case "litersPerSecond":
            return None
        case "lumens":
            return None
        case "luxes":
            return LIGHT_LUX
        case "megabecquerels":
            return None
        case "megaBtus":
            return None
        case "megahertz":
            return UnitOfFrequency.MEGAHERTZ
        case "megajoules":
            return UnitOfEnergy.MEGA_JOULE
        case "megajoulesPerDegreeKelvin":
            return None
        case "megajoulesPerKilogramDryAir":
            return None
        case "megajoulesPerSquareFoot":
            return None
        case "megajoulesPerSquareMeter":
            return None
        case "megavoltAmpereHours":
            return None
        case "megavoltAmpereHoursReactive":
            return None
        case "megavoltAmperes":
            return None
        case "megavoltAmperesReactive":
            return None
        case "megavolts":
            return None
        case "megawattHours":
            return UnitOfEnergy.MEGA_WATT_HOUR
        case "megawattHoursReactive":
            return None
        case "megawatts":
            return None
        case "megohms":
            return None
        case "meters":
            return UnitOfLength.METERS
        case "metersPerHour":
            return None
        case "metersPerMinute":
            return None
        case "metersPerSecond":
            return UnitOfSpeed.METERS_PER_SECOND
        case "metersPerSecondPerSecond":
            return None
        case "microgramsPerCubicMeter":
            return CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
        case "microgramsPerLiter":
            return None
        case "microgray":
            return None
        case "micrometers":
            return None
        case "microSiemens":
            return None
        case "microsieverts":
            return None
        case "microsievertsPerHour":
            return None
        case "milesPerHour":
            return UnitOfSpeed.MILES_PER_HOUR
        case "milliamperes":
            return UnitOfElectricCurrent.MILLIAMPERE
        case "millibars":
            return UnitOfPressure.MBAR
        case "milligrams":
            return UnitOfMass.MILLIGRAMS
        case "milligramsPerCubicMeter":
            return CONCENTRATION_MILLIGRAMS_PER_CUBIC_METER
        case "milligramsPerGram":
            return None
        case "milligramsPerKilogram":
            return None
        case "milligramsPerLiter":
            return None
        case "milligray":
            return None
        case "milliliters":
            return UnitOfVolume.MILLILITERS
        case "millilitersPerSecond":
            return None
        case "millimeters":
            return UnitOfLength.MILLIMETERS
        case "millimetersOfMercury":
            return None
        case "millimetersOfWater":
            return UnitOfPrecipitationDepth.MILLIMETERS
        case "millimetersPerMinute":
            return None
        case "millimetersPerSecond":
            return None
        case "milliohms":
            return None
        case "milliseconds":
            return UnitOfTime.MILLISECONDS
        case "millisiemens":
            return None
        case "millisieverts":
            return None
        case "millivolts":
            return UnitOfElectricPotential.MILLIVOLT
        case "milliwatts":
            return None
        case "minutes":
            return UnitOfTime.MINUTES
        case "minutesPerDegreeKelvin":
            return None
        case "months":
            return UnitOfTime.MONTHS
        case "nanogramsPerCubicMeter":
            return None
        case "nephelometricTurbidityUnit":
            return None
        case "newton":
            return None
        case "newtonMeters":
            return None
        case "newtonSeconds":
            return None
        case "newtonsPerMeter":
            return None
        case "noUnits":
            return None
        case "ohmMeterPerSquareMeter":
            return None
        case "ohmMeters":
            return None
        case "ohms":
            return None
        case "partsPerBillion":
            return CONCENTRATION_PARTS_PER_BILLION
        case "partsPerMillion":
            return CONCENTRATION_PARTS_PER_MILLION
        case "pascals":
            return UnitOfPressure.PA
        case "pascalSeconds":
            return None
        case "percent":
            return PERCENTAGE
        case "percentObscurationPerFoot":
            return None
        case "percentObscurationPerMeter":
            return None
        case "percentPerSecond":
            return None
        case "percentRelativeHumidity":
            return PERCENTAGE
        case "perHour":
            return None
        case "perMille":
            return None
        case "perMinute":
            return None
        case "perSecond":
            return None
        case "pH":
            return None
        case "poundsForcePerSquareInch":
            return UnitOfPressure.PSI
        case "poundsMass":
            return UnitOfMass.POUNDS
        case "poundsMassPerHour":
            return None
        case "poundsMassPerMinute":
            return None
        case "poundsMassPerSecond":
            return None
        case "powerFactor":
            return None
        case "psiPerDegreeFahrenheit":
            return None
        case "radians":
            return None
        case "radiansPerSecond":
            return None
        case "revolutionsPerMinute":
            return REVOLUTIONS_PER_MINUTE
        case "seconds":
            return UnitOfTime.SECONDS
        case "siemens":
            return None
        case "siemensPerMeter":
            return None
        case "sieverts":
            return None
        case "squareCentimeters":
            return None
        case "squareFeet":
            return None
        case "squareInches":
            return None
        case "squareMeters":
            return UnitOfArea.SQUARE_METERS
        case "squareMetersPerNewton":
            return None
        case "teslas":
            return None
        case "therms":
            return None
        case "tonHours":
            return None
        case "tons":
            return None
        case "tonsPerHour":
            return None
        case "tonsRefrigeration":
            return None
        case "usGallons":
            return UnitOfVolume.GALLONS
        case "usGallonsPerHour":
            return None
        case "usGallonsPerMinute":
            return UnitOfVolumeFlowRate.GALLONS_PER_MINUTE
        case "voltAmpereHours":
            return None
        case "voltAmpereHoursReactive":
            return UnitOfReactivePower.VOLT_AMPERE_REACTIVE
        case "voltAmperes":
            return None
        case "voltAmperesReactive":
            return None
        case "volts":
            return UnitOfElectricPotential.VOLT
        case "voltsPerDegreeKelvin":
            return None
        case "voltsPerMeter":
            return None
        case "voltsSquareHours":
            return None
        case "wattHours":
            return UnitOfEnergy.WATT_HOUR
        case "wattHoursPerCubicMeter":
            return None
        case "wattHoursReactive":
            return None
        case "watts":
            return UnitOfPower.WATT
        case "wattsPerMeterPerDegreeKelvin":
            return None
        case "wattsPerSquareFoot":
            return None
        case "wattsPerSquareMeter":
            return UnitOfIrradiance.WATTS_PER_SQUARE_METER
        case "wattsPerSquareMeterDegreeKelvin":
            return None
        case "webers":
            return None
        case "weeks":
            return UnitOfTime.WEEKS
        case "years":
            return UnitOfTime.YEARS
        case _:
            return None


def bacnet_to_device_class(
    unit_in: str | None,
    device_class_units: Mapping[
        SensorDeviceClass, Collection[type[StrEnum] | str | None]
    ],
) -> str | None:
    """BACnet engineering unit to device class"""
    if unit := bacnet_to_ha_units(unit_in):
        for classes, values in device_class_units.items():
            if unit in values:
                return classes
    else:
        return None


def decimal_places_needed(resolution: float) -> int:
    if resolution <= 0:
        raise ValueError("Resolution must be greater than 0")

    # Take the base-10 logarithm of the resolution
    log10_value = -math.log10(resolution)

    # Take the ceiling of the logarithm value
    decimal_places = math.ceil(log10_value)

    return decimal_places
