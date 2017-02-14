from esp8266_i2c_lcd import I2cLcd
import machine, time, dht
import vcnl4010 as ALPSensor
import tmp007 as TempSensor
import MABuffer as MA


## Interval Variables for embed, declared as global variables

# Embed-related interfaces/tools 
i2c = machine.I2C(scl = machine.Pin(5), sda = machine.Pin(4), freq = 100000)
rtc = machine.RTC()

# I/O (Sensors, LCD, etc.)
alpsensor = ALPSensor.ALPSensor(i2c)
tempsensor = TempSensor.TempSensor(0x40, i2c)
humidsensor = dht.DHT11(machine.Pin(13))
moistsensor = machine.ADC(0)
lcd = I2cLcd(i2c, 0x27, 2, 16)
watersensor = { 'vcc': machine.Pin(16,machine.Pin.OUT) , 'sense':machine.Pin(2, machine.Pin.IN)}
pumpcontroller = machine.PWM(machine.Pin(12), freq = 50, duty = 52)
lightingcontroller = machine.PWM(machine.Pin(15), freq = 60, duty = 0)

# Moving average buffers for measurements
ALbuffer = MA.Buffer(5)
proxbuffer = MA.Buffer(5)
tempbuffer = MA.Buffer(5)
humidbuffer = MA.Buffer(5)
moistbuffer = MA.Buffer(5)

# curr desired profile settings for the greenhouse
plantsettings =	{
					'Profile' : 'basil',
					'Light_low' : 1000,
					'Light_upp' : 1200,
					'Temp_low': 25,
					'Temp_upp': 28,
					'Humidity_low' : 67,
					'Humidity_upp' : 78,
					'Moisture_low' : 200,
					'Moisture_upp' : 500,
					'Shutdown' : 0,
					}

# Specialized callback functions based on command given by client
def readAmbient():
	return ALbuffer.getMA()

def readProx():
	return proxbuffer.getMA()

def readTemp():
	return tempbuffer.getMA()

def readHumidity():
	return humidbuffer.getMA()

def readMoisture():
	return moistbuffer.getMA()

def readProfile():
	return heap[0]

def setTime(_timestamp):
	timestamp = _timestamp.split("_")
	Y, M, D = [int(i) for i in timestamp[0].split("-")]
	h, m, s = [int(i) for i in timestamp[1].split(".")[0].split(":")]
	rtc.datetime((Y,M,D,0,h,m,s,0))
	return "Success"

# str -> function mapping, to be used in on_message
read_func_map = 	{
					'profile' : readProfile,
					'ambient' : readAmbient,
					'prox' : readProx,
					'temp' : readTemp,
					'humid' : readHumidity,
					'moisture' : readMoisture,
					}

# LCD State FSM, to iterate through the LCD
next_print_state = 	{
					'Profile' : 'Light',
					'Light' : 'Temp',
					'Temp' : 'Humidity',
					'Humidity' : "Moisture",
					"Moisture" : "Profile",
					}


warning_status = 	{
					'low_light' : False,
					'high_light' : False,
					'low_temp' : False,
					'high_temp' : False,
					'low_humid' : False,
					'high_humid' : False,
					'low_moist' : False,
					'high_moist' : False,
					'low_water' : False,
					}

heap = []