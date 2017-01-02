#! /usr/bin/env python
# -*- coding: utf-8 -*-

# A DS1621 has three address pins A2, A1, A0. 
# A DS16221 with all address pins tied to ground will have A2A1A0 = 000;  
# That chip will appear at I2C bus address 0x48. 
# Another DS1621 with A2A1A0 = 001 (A0 to Vdd) will be at 0x49, and so on. 
#
# sensornames and addresses must be declared in calling module, or in main().
# example:
# Room    = 0x48  
# Remote  = 0x49  

from __future__ import division # to calculate a float from integers
import smbus, time

# DS1621 commands
START           = 0xEE
STOP            = 0x22
READ_TEMP       = 0xAA
READ_COUNTER    = 0xA8
READ_SLOPE      = 0xA9
ACCESS_CONFIG   = 0xAC
ACCESS_TH       = 0xA1
ACCESS_TL       = 0xA2

# read-only status bits
DONE      = 0x80
TH_BIT    = 0x40
TL_BIT    = 0x20
NVB       = 0x10 # Non-Volatile memory Busy

# r/w status bits (bit masks)
POL_HI    = 0x02
POL_LO    = 0xFD
ONE_SHOT  = 0x01
CONT_MODE = 0xFE
CLR_TL_TH = 0x9F

# assist functions
def twos_comp(byte):
    '''input byte in two's complement is returned as signed integer. '''
    if len(bin(byte)[2:]) > 8:
        # shouldn't ever get here
        print '\nWarning: input ' + str(hex(byte)) + \
              ' truncated to least significant byte: ' + \
              str(hex(0xFF & byte))
        byte = 0xFF & byte
    return ~(255 - byte) if byte > 127 else byte

def decode_DS(word):
    ''' 2-byte data from DS1621 is received as LSB MSB
        MSB is a two's complement number from -55 to +125
        If leftmost bit from LSB is set, add .5 to reading. '''
     
    LSB = word // 256  # integer division with two // because we're using division from Python 3
    MSB = word % 256
    value = twos_comp(MSB)
    return value + .5 if LSB == 128 else value + .0

def encode_DS(num):
    ''' 2-byte thermostat setting sent to DS1621
        in same format as data received, see decode_DS, above.
    '''
    # warn for out of range and set within range. 
    if num < -55: 
        print '\nWarning: input ' + str(num) + ' out of range, set to -55'
        num = -55
    if num > 125:
        print '\nWarning: input ' + str(num) + ' out of range, set to 125'
        num = 125

    # round off to nearest .5
    num = round(num*2)/2.0
    MSB = int(num)
    decimal = num - MSB

    # LSB is binary 1000.0000 if decimal = .5, otherwise 0
    # data is sent LSB MSB
    if decimal == 0:
        return MSB
    else:
        if MSB > 0:
            return MSB | 0x8000
        else:
            return (MSB - 1) & 0x80FF 

# General read function, also updates a register  
def read_degreesC_byte(bus, sensor):
    '''returns temperature in degrees Celsius as integer '''
        
    bus.read_byte_data(sensor, START)
    degreesC_byte = twos_comp(bus.read_byte_data(sensor, READ_TEMP))
    return degreesC_byte             
            
# Oneshot read functions all give a START command.  
def read_degreesC_all_oneshot(bus, sensor):
    '''returns temperature in degrees Celsius, 
        as integer,
        as same reading with added half degree precision
        and with high(er) resolution, as per DS1621 datasheet '''
        
    bus.read_byte_data(sensor, START)

    degreesC_byte = twos_comp(bus.read_byte_data(sensor, READ_TEMP))
        
    degreesC_word = decode_DS(bus.read_word_data(sensor, READ_TEMP))

    slope = bus.read_byte_data(sensor, READ_SLOPE)
    counter = bus.read_byte_data(sensor, READ_COUNTER)
    degreesC_HR = degreesC_byte - .25 + (slope - counter)/slope
    #~ print slope, counter, slope - counter, (slope - counter)/slope 
    
    return degreesC_byte, degreesC_word, degreesC_HR
    
def read_degreesC_hiRes_oneshot(bus, sensor): 
    '''returns temperature as high-res value, as per DS1621 datasheet''' 
    
    bus.read_byte_data(sensor, START)
    
    degreesC_byte = twos_comp(bus.read_byte_data(sensor, READ_TEMP))

    slope = bus.read_byte_data(sensor, READ_SLOPE)
    counter = bus.read_byte_data(sensor, READ_COUNTER)
    degreesC_HR = degreesC_byte - .25 + (slope - counter)/slope

    return degreesC_HR

# Continuous read function DOES NOT give a START command
# the START command for Continuous mode is given by set_mode(Continous)    
def read_degreesC_continous(bus, sensor):
    '''returns temperature in degrees Celsius, 
        as integer,
        as same reading with added half degree precision
        and with high(er) resolution, as per DS1621 datasheet '''
        
    degreesC_byte = twos_comp(bus.read_byte_data(sensor, READ_TEMP))
    degreesC_word = decode_DS(bus.read_word_data(sensor, READ_TEMP))

    slope = bus.read_byte_data(sensor, READ_SLOPE)
    counter = bus.read_byte_data(sensor, READ_COUNTER)
    degreesC_HR = degreesC_byte - .25 + (slope - counter)/slope

    return degreesC_byte, degreesC_word, degreesC_HR

# Continuous mode needs a stop-conversion command    
def stop_conversion(bus, sensor): 
    bus.read_byte_data(sensor, STOP)

def read_config(bus, sensor):
    Conf = bus.read_byte_data(sensor, ACCESS_CONFIG)

    TH = decode_DS(bus.read_word_data(sensor, ACCESS_TH))
    TL = decode_DS(bus.read_word_data(sensor, ACCESS_TL))
    
    if Conf & POL_HI:
        level, device = 'HIGH', 'cooler' 
    else: 
        level, device = 'LOW', 'heater'  

    Rpt = '''\n  Status of DS1621 at address {sensor}:
    \tConversion is {convstat}
    \t{have_th} measured {th} degrees Celsius or more
    \t{have_tl} measured below {tl} degrees Celsius
    \tNon-volatile memory is {busy}
    \tThermostat output is Active {level} (1 turns the {device} on)
    \tMeasuring mode is {mode}'''

    print Rpt.format(
            sensor = hex(sensor),
            convstat = 'done' if Conf & DONE else 'in process',
            have_th = 'HAVE' if Conf & TH_BIT else 'have NOT', 
            th = TH, 
            have_tl = 'HAVE' if Conf & TL_BIT else 'have NOT', 
            tl = TL,
            busy = 'BUSY' if Conf & NVB else 'not busy',
            level = level, 
            device = device,
            mode = 'One-Shot' if Conf & ONE_SHOT else 'Continuous', 
            )
         
    return Conf, TH, TL

def get_thermostat(bus, sensor):
    '''returns low and high thermostat settings'''
    low_therm = decode_DS(bus.read_word_data(sensor, ACCESS_TL))
    hi_therm = decode_DS(bus.read_word_data(sensor, ACCESS_TH))
    return low_therm, hi_therm

# write helper    
def wait_NVM(bus, sensor):
    newConf = bus.read_byte_data(sensor, ACCESS_CONFIG)
    # wait for write to Non-Volatile Memory to finish 
    while newConf & NVB: 
        newConf = bus.read_byte_data(sensor, ACCESS_CONFIG)
    return 
    
def write_conf_byte(bus, sensor, byte): 
    bus.write_byte_data(sensor, ACCESS_CONFIG, byte)
    wait_NVM(bus, sensor)
    return 

def set_thermostat(bus, sensor, lower, upper):
    ''' set new lower and upper thermostat limits for thermostat pin
        in non-volatile memory; also reset TH and TH bits. 
    '''
    bus.write_word_data(sensor, ACCESS_TL, encode_DS(lower))
    bus.write_word_data(sensor, ACCESS_TH, encode_DS(upper))
    wait_NVM(bus, sensor)
    
    Conf = bus.read_byte_data(sensor, ACCESS_CONFIG) & CLR_TL_TH
    write_conf_byte(bus, sensor, Conf)
    
    # take a reading to update the thermostat register
    read_degreesC_byte(bus, sensor)
    
    return

def set_thermohyst(bus, sensor, upper, hyst=0.5):
    ''' set upper temp with a hysteresis for thermostat pin
        and reset TH and TH bits. 
    '''
    set_thermostat(bus, sensor, upper - hyst, upper)
    return
    
def set_mode(bus, sensor, mode):
    if mode == 'Continuous':
        Conf = bus.read_byte_data(sensor, ACCESS_CONFIG) & CONT_MODE
        write_conf_byte(bus, sensor, Conf)
        bus.read_byte_data(sensor, START)
        
    elif mode == 'OneShot':    
        Conf = bus.read_byte_data(sensor, ACCESS_CONFIG) | ONE_SHOT
        write_conf_byte(bus, sensor, Conf)
        
    else:
        print 'Unknown mode: {}'.format(mode)
        
    return
        
def set_thermoLOW(bus, sensor, LOW=True): 
    Conf = bus.read_byte_data(sensor, ACCESS_CONFIG)
    Conf = Conf & POL_LO if LOW else Conf | POL_HI  
        
    write_conf_byte(bus, sensor, Conf)
    
    # take a reading to update the thermostat register
    read_degreesC_byte(bus, sensor)
    
    return
    
def read_logline(bus, sensor, name):
    reading = read_degreesC_all_oneshot(bus, sensor)
    return '\tSensor name: {:8} {:3} | {:5.1f} | {:7.3f}'.format(name, *reading)

def wake_up(bus, sensor):
    ''' Device always starts in Idle mode, first reading is not usable.'''
    read_degreesC_byte(bus, sensor)
    time.sleep(0.6)
    
def main():
    # just initialise what's on the bus, show settings and take a reading. 
    
    # must instantiate the bus. 
    # on RPi 256 MB version, it's called i2c_0
    # on RPi 512 MB version, it's called i2c_1
    # just for clarity, use those names
    i2c_0 = smbus.SMBus(0)

    # sensorname at bus address.
    Room = 0x48

    # First reading after startup is not usable, only wakes the devices up. 
    ds.wake_up(i2c_0, Room)

    # show chip configuration
    read_config(i2c_0, Room)
    
    s = '''\n  Sensorname {}:
    \tas integer: {}
    \twith .5 resolution: {}
    \thigh-res: {}'''
    
    print s.format('Room', *read_degreesC_all_oneshot(i2c_0, Room))
    
if __name__ == "__main__":
    main()
