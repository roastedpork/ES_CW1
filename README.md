# ES_CW1
Repository for EE3-24 Embedded Systems Coursework 1

## Prequisites for the coursework

### Bash on Windows (highly recommended)
Install [Bash on Windows](http://www.howtogeek.com/249966/how-to-install-and-use-the-linux-bash-shell-on-windows-10/), or dual-boot a Linux VM for this coursework.

### ESP8266 WiFi Microcontroller
Datasheet for the microcontroller can be found [here](http://download.arduino.org/products/UNOWIFI/0A-ESP8266-Datasheet-EN-v4.3.pdf). 
There is no driver implementation for the microcontroller, which might reuqire us to implement our own code for it. 

### Installing Micropython interpreter (ampy)
Instructions for installing ampy can be found [here](https://github.com/adafruit/ampy).  
The documentation for using I<sup>2</sup>C on the ESP8266 can be found [here](http://docs.micropython.org/en/latest/esp8266/library/machine.I2C.html). 

### I<sup>2</sup>C Interface
Refer to lecture 2 slides for specifics details of the interface. Most importantly, ensure that SCLK and SDA pins are connected correctly onto the mbed. 

## Architecture

### Embed

### Designated Sensor

### Interaction with server via WiFis