# -*- coding: utf-8 -*-

from DS1621 import *

# you must instantiate the bus. 
# on RPi 256 MB version, it's called i2c_0
# on RPi 512 MB version, it's called i2c_1
# just for clarity, use those names
i2c_0 = smbus.SMBus(0)

# sensors with their bus addresses, see above
Room    = 0x48

# The first reading after startup is not usable, only wakes the devices up. 
read_degreesC(i2c_0, Room)
time.sleep(0.6) # allow some wake-up time. Tweaked for shortest time. 

# set_1shot(i2c_0, Room)
# set_continuous(i2c_0, Room)

# show chip configuration
read_config(i2c_0, Room)

# set upper and lower thermostat limits.
# decimals are rounded to the nearest .5
# set_thermostat(i2c_0, Room, 5.32, 17.23)

# set thermostat limits with upper temp and default hysteresis
# set_thermohyst(i2c_0, Room, 19)

# set thermostat pin active Low (default)
# set_thermoLOW(i2c_0, Room)

# set_thermoLOW(i2c_0, Room, False)
# read_config(i2c_0, Room)

# show thermostat settings
# s = '\n\tThermostat low: {} °C\n\tThermostat high: {} °C'
# print s.format(*get_thermostat(i2c_0, Room)).decode('utf-8')

# read high resolution temperature
# print read_degreesC_hiRes(i2c_0, Room)

# Show temperature in all available resolutions
s = '''\n  Sensor name {}:
    \tas integer: {}
    \twith .5 resolution: {}
    \thigh-res: {}'''
    
print s.format('Room', *read_degreesC(i2c_0, Room))

