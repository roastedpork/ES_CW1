# ES_CW1
Repository for EE3-24 Embedded Systems Coursework 1


## Current List of To Dos

+ ~~Figure out how to interface the embed~~
+ ~~Figure out how to get the embed to communicate with the sensor~~
+ Get proper raw measurements from the sensor
+ Convert raw data into a form that makes sense
+ Design an IoT application for the sensor

## Prequisites for the coursework

### Windows Setup

~~Install [Bash on Windows](http://www.howtogeek.com/249966/how-to-install-and-use-the-linux-bash-shell-on-windows-10/), or dual-boot a Linux VM for this coursework.~~

So apparently there is an issue with Bash on Windows with regards to connecting to its serial ports.
Follow the instructions [here](https://learn.adafruit.com/adafruit-feather-huzzah-esp8266/overview) for windows machines.

Install python 2.7/3.6 for Windows, and install PuTTY in order to access the serial port.

General setup documentation can be found [here] (https://learn.adafruit.com/micropython-basics-how-to-load-micropython-on-a-board/overview) 

To setup Micropython Read-Evaluate-Print Loop (REPL) can be found [here] (https://learn.adafruit.com/micropython-basics-how-to-load-micropython-on-a-board/serial-terminal) 

Drivers to install for windows for ESP8226 can be found [here] (https://www.silabs.com/products/mcu/Pages/USBtoUARTBridgeVCPDrivers.aspx)

Ampy failure troubleshoot can be found [here] (https://forum.micropython.org/viewtopic.php?t=2702) 

In summary:
+ Python - To install relevant micropython packages
+ Serial driver - To allow PuTTY to work later on
+ PuTTY - To get a real-time output from the embed
+ ampy - File manager for the embed which can be accessed via Windows command prompt

### How to use Git
You need to setup an RSA key to be able to SSH into the git repository. 
Alternatively, you can clone the repository via HTTPS, which requires you so fill in your login details everytime you push something in.

#### Basic setup for Git 
```
sudo apt-get install git
git clone https://github.com/roastedpork/ES_CW1.git
```

#### Commiting to Git
```
git add --all
git commit -m "<insert your message here>"
git push
```

### ESP8266 WiFi Microcontroller
Datasheet for the microcontroller can be found [here](http://download.arduino.org/products/UNOWIFI/0A-ESP8266-Datasheet-EN-v4.3.pdf). 
There is no driver implementation for the microcontroller, which might require us to implement our own code for it. 

### Windows Setup for Interfacing
General setup documentation to load Micropython into the board can be found [here] (https://learn.adafruit.com/micropython-basics-how-to-load-micropython-on-a-board/overview) 

To setup Micropython Read-Evaluate-Print Loop (REPL) can be found [here] (https://learn.adafruit.com/micropython-basics-how-to-load-micropython-on-a-board/serial-terminal) 

Drivers to install for windows for ESP8266 can be found [here] (https://www.silabs.com/products/mcu/Pages/USBtoUARTBridgeVCPDrivers.aspx)

Ampy failure troubleshoot can be found [here] (https://forum.micropython.org/viewtopic.php?t=2702) 

Instructions for installing ampy can be found [here](https://github.com/adafruit/ampy).  
The documentation for using I<sup>2</sup>C on the ESP8266 can be found [here](http://docs.micropython.org/en/latest/esp8266/library/machine.I2C.html). 

#### Test script to check if setup successful:
```python 
import machine, time 
led = machine.Pin(0,machine.Pin.OUT)
while True:
	led.high()
	time.sleep(1.0)
	led.low() 
	time.sleep(1.0)
```

### I<sup>2</sup>C Interface
Refer to lecture 2 slides for specifics details of the interface. 
Most importantly, ensure that SCLK and SDA pins are connected correctly onto the mbed. 

## Architecture

### Embed 
Adafruit Feather HUZZAH ESP8266 PINOUT Diagram
![Figure1-1 Embed Pinout](images/adafruit_products_pinbottom.jpg)

### Designated Sensor

A Sensor class for the Light and Proximity Sensor was created in vcnl4010.py, that is able to convert the reading from the sensor into a raw integer value.

### Interaction with server via WiFis using MQTT
The documentation for MQTT can be found [here](https://github.com/mqtt/mqtt.github.io). 
This should be used as a basic message passing interface on top of the WiFi hardware.

<<<<<<< HEAD
=======

>>>>>>> 654abae2542495f8c04964c1e0a195c1b5af541a
