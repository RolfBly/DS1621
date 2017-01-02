#! /usr/bin/python
# -*- coding: utf-8 -*-

# todo: 
# separate functions for init, continuous and one-shot
# in continuous mode lijken de bits voor heb boven en heb onder gemeten niks te doen. 

from __future__ import division # to calculate a float from integers
import smbus, time

import DS1621 as ds

# must instantiate the bus. 
# on RPi 256 MB version, it's called i2c_0
# on RPi 512 MB version, it's called i2c_1
# just for clarity, use those names
i2c_0 = smbus.SMBus(0)

# sensorname at bus address.
Room = 0x48

# First reading after startup is not usable, only wakes the devices up. 
ds.wake_up(i2c_0, Room)

##   Continuous mode is useful if you want to use the thermostat pin
##   with rapidly changing temperatures e.g. inside an enclosure

### In Continuous mode, you can set hysteresis in two ways. 

# upper and lower thermostat limits, decimals are rounded to the nearest .5
ds.set_thermostat(i2c_0, Room, 10.0, 25.5)

# show settings
ds.read_config(i2c_0, Room)

# show thermostat settings
thermosettings = '\n\tThermostat low: {} °C\n\tThermostat high: {} °C'
print thermosettings.format(*ds.get_thermostat(i2c_0, Room)).decode('utf-8')

### Alternatively, set upper limit and hysteresis delta, default = .5 C

# ds.set_thermohyst(i2c_0, Room, 19)

## Thermostat pin active High turns the cooler on

# set thermostat pin active High
# ds.set_thermoLOW(i2c_0, Room, LOW=False)

# set continuous measurement mode and start converting 
# ds.set_mode(i2c_0, Room, 'Continuous')

