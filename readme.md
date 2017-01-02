## DS1621.py Readme  

Python library for Maxim/Dallas DS1621 I2C temperature sensor, originally written for Raspberry Pi's I2C-bus.  

### Functional description  

#### Primary functions  
 
- Read temperature with 3 precisions  
- Read high-resolution temperature (is one of the 3)  
- Read & verbosely report status register  
- Set measurement mode to Continuous or One Shot  
- Stop conversion command to end a Continuous session.  

Reading in One-shot mode issues a start command, takes a reading, and then leaves the device idle.  

Setting to Continous mode issues a start command. You can then take a any number of readings, until you issue a stop conversion command. For more information, see the DS1621 datasheet.  

#### Functions for the thermostat pin on the DS1621  

- Get thermostat setting from DS1621 non-volatile memory  
- Set thermostat High and Low temperature  
- Set thermohyst, same but with high temp and hysteresis  
- Set thermoLOW makes thermostat pin active Low (1 = heater on)  
- Set thermoLOW False makes thermostat pin active High (1 = cooler on)  

#### Assist functions for converting to and from the DS's register format  

- range is -55 to +125 degrees Celsius with .5 resolution  
- data format is LSB MSB  
- MSB is desired temperature in two's complement  
- LSB is 0x80 for an additional .5 degrees.  

### Dependencies  

smbus  

### Furthermore  

datalog.py is a simple script for taking and logging temperature readings. This is useful for calibrating the device, for example if it's mounted near a more or less constant heat source that offsets the reading.  

### How to use  

A sensor more or less directly mounted on or near a Raspberry Pi will be heated up by the RPi and may read several degrees higher than the actual room temperature. You can find out more about maximum cable length for the I2C-bus [here][I2C].  
    
Just for clarity, this is the chips pinout:  

               _____  
        SDA - 1     8 - Vdd  
        SCL - 2     7 - A0  
       Tout - 3     6 - A1  
        GND - 4_____5 - A2  

Recommended reading is Maxim's [datasheet][datasheet].  

A DS1621 with address pins A2A1A0 = 000 (all tied to GND) will appear at bus address 0x48. Another DS1621 with A2A1A0 = 001 (A0 to Vdd) will be at 0x49, and so on.  

Sensornames should be declared in the calling module or in main(), for example:  

    Room    = 0x48  
    Remote  = 0x49  

Using RPi's GPIO (which includes I2C) requires root rights. Run the the driver with elevation like this:  

    $ sudo python DS1621.py  

You can also run it with indirect elevation with this script:  

    #! /usr/bin/env python  
    # -*- coding: utf-8 -*-  

    import subprocess  

    subprocess.call(['sudo', './DS1621.py'])  

In both cases however, the user who issues the command or launches the script, must be a sudoer.  

Tighter security is possible with this [workaround][workaround]. Essentially, you make the GPIO memory belong to group `gpio`, and then make your DS1621 user a member of `gpio` and `i2c`.  
<quote>
Check that /dev/gpiomem has the correct permissions.  

    $ ls -l /dev/gpiomem  
    crw-rw---- 1 root gpio 244, 0 Dec 28 22:51 /dev/gpiomem  

If it doesn't then set the correct permissions as follows  

    sudo chown root.gpio /dev/gpiomem  
    sudo chmod g+rw /dev/gpiomem  
</quote>  

[datasheet]: http://pdfserv.maximintegrated.com/en/ds/DS1621.pdf  
[I2C]: http://electronics.stackexchange.com/questions/106265/maximum-i2c-bus-length  
[workaround]: http://raspberrypi.stackexchange.com/a/40106/2995  
