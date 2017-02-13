from umqtt.simple import MQTTClient
from esp8266_i2c_lcd import I2cLcd
import machine, time, json, dht
import vcnl4010 as ALPSensor
import tmp007 as TempSensor
import MABuffer as MA
import MQTTWrapper
import network


## Interval Variables for embed, declared as global variables

# Embed-related interfaces/tools 
i2c = machine.I2C(scl = machine.Pin(5), sda = machine.Pin(4), freq = 100000)
rtc = machine.RTC()
client = MQTTWrapper.MQTTWrapper('192.168.1.15', 'PLUSNET-6QTFPK', '7dff6ec6df', on_message) #'192.168.0.10', 'EEERover', 'exhibition') #

# I/O (Sensors, LCD, etc.)
alpsensor = ALPSensor.ALPSensor(i2c)
tempsensor = TempSensor.TempSensor(0x40, i2c)
humidsensor = dht.DHT11(machine.Pin(13))
lcd = I2cLcd(i2c, 0x27, 2, 16)
# watersensor = 
# fancontroller = 
# lightingcontroller = 

# Moving average buffers for measurements
AL_buffer = MA.Buffer()
prox_buffer = MA.Buffer()
temp_buffer = MA.Buffer()
humid_buffer = MA.Buffer()
moist_buffer = MA.Buffer()

# curr desired profile settings for the greenhouse
plant_settings =	{
					'Profile' : 'basil',
					'Light_low' : 1000,
					'Light_upp' : 1200,
					'Temp_low', 25,
					'Temp_upp', 28,
					'Humidity_low' : 67,
					'Humidity_upp' : 78,
					'Moisture_low' : 200,
					'Moisture_upp' : 500,
					}


# Callback function when embed receives a message from a client
def on_message(topic, msg):
    # Process command based on message arguments
	recv_data = json.loads(str(msg,'utf-8'))
	resp = {'type' : recv_data['type'] + '_RESPONSE', 'data' = {}}

	## Processes client message based on type of message
	# If msg is a request for curr data
	if recv_data['type'] == 'READ':
		for cmd in recv_data['data']:
			try:
				resp['data'][cmd] = read_func_map[cmd]()	
			except KeyError:
				pass

	# If msg is a request to set the embed clock
	elif recv_data['type'] == "SET_TIME":
		resp['data']['timesync'] = setTime(recv_data['timestamp'])
	
	# If msg is a request to set a certain control parameter
	elif recv_data['type'] == "SET":
		try:
			_type, _value = recv_data['data']
			plant_settings[_type] = _value
			resp['data']['set_resp'] = '"%s" parameter successfully changed to "%f"' % (_type,_value)
		
		except KeyError:
			resp['data']['set_resp'] = 'There is no "%s" control parameter' % (_type)
			
		except ValueError:
			resp['data']['set_resp'] = 'Not enough values provided (This should not happen)'

	# If msg is a request to change the plant profile
	elif recv_data['type'] == "PROFILE":
		new_profile = recv_data['data']

		# Check if the new profile only contains all the valid fields, changes profile if true
		if set(plant_settings.keys()) == set(new_profile.keys()):
			plant_settings = new_profile
			resp['data']['profile_resp'] = 'Profile has been changed to "%s"' % (plant_settings['Profile'])

		else:
			resp['data']['profile_resp'] = 'Could not change the plant profile'



	# Sending response back to the client
	timestamp = "%d-%d-%d_%d:%d:%d" % (time.localtime()[:6])
	resp['timestamp'] = timestamp
	client.sendData("response", resp)
    

# Specialized callback functions based on command given by client
def readAmbient():
	return AL_buffer.getMA()

def readProx():
	return prox_buffer.getMA()

def readTemp():
	return temp_buffer.getMA()

def readHumidity():
	return humid_buffer.getMA()

def readMoisture():
	pass

def setTime(_timestamp):
	timestamp = _timestamp.split("_")
	Y, M, D = [int(i) for i in timestamp[0].split("-")]
	h, m, s = [int(i) for i in timestamp[1].split(".")[0].split(":")]
	rtc.datetime((Y,M,D,0,h,m,s,0))
	return "Success"

# str -> function mapping, to be used in on_message
read_func_map = 	{
					'ambient' : readAmbient,
					'prox' : readProx,
					'temp' : readTemp,
					'humid' : readHumidity,
					# 'moisture' : readMoisture,
					}

# LCD State FSM, to iterate through the LCD
next_print_state = 	{
					'Profile' : 'Light',
					'Light' : 'Temp',
					'Temp' : 'Humidity',
					'Humidity' : "Moisture",
					"Moisture" : "Profile",
					}


## Main Function!
if __name__ == "__main__":
	rtc.alarm(0,1000)
	state = next_print_state['Humidity']
	value = ""
	count = 0
	i = 0
	while 1:
		# Asynchronous means the embed to can perform other things while listening
		client.listenAsync() 
		
		## Performs this loop every second
		if rtc.alarm_left() <= 0:
			
			# Adds a new set of readings in the moving average buffers
			AL_buffer.update(alpsensor.getALReading())
			prox_buffer.update(alpsensor.getProxReading())
			temp_buffer.update(tempsensor.read())
			humidsensor.measure()
			humid_buffer.update(humidsensor.humidity())

			# Changes LCD Display every 5 seconds
			if count % 5 == 0:
				state = next_print_state[state]
				
				if state == 'Profile':
					value = plant_settings[state]
				elif state == 'Light':
					value = str(round(AL_buffer.getMA(),2)) + " lux"
				elif state == 'Temp':
					value = str(round(temp_buffer.getMA(),2)) + " degs"
				elif state == 'Humidity':
					value = str(round(humid_buffer.getMA(),2)) + "%"
				elif state == 'Moisture':
					value = str(round(moist_buffer.getMA(),2))


				lcd.clear()
				lcd.move_to(0,0)
				lcd.putstr("%s: \n%s" %(state,value))


			count += 1
			rtc.alarm(0,1000)

		## Control Loop goes here
