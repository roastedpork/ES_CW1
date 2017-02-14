from umqtt.simple import MQTTClient
from esp8266_i2c_lcd import I2cLcd
import machine, time, json, dht
import vcnl4010 as ALPSensor
import tmp007 as TempSensor
import MABuffer as MA
import MQTTWrapper
import network
import uheapq
import gc

# Enables garbage collection for heap
gc.enable()


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

# Runs garbage collection before allocation onto heap
gc.collect()
heap = []
uheapq.heappush(heap, plantsettings)

# Callback function when embed receives a message from a client
def on_message(topic, msg):
    # Process command based on message arguments
	recv_data = json.loads(str(msg,'utf-8'))
	resp = {'type' : recv_data['type'] + '_RESPONSE', 'data' : {}}

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
			plantsettings = uheapq.heappop(heap)
			if _type in plantsettings.keys():
				plantsettings[_type] = _value
				resp['data']['set_resp'] = '"%s" parameter successfully changed to "%f"' % (_type,_value)
			else:
				resp['data']['set_resp'] = 'There is no "%s" control parameter' % (_type)
			
			uheapq.heappush(heap,plantsettings)
		except ValueError:
			resp['data']['set_resp'] = 'Not enough values provided (This should not happen)'

	# If msg is a request to change the plant profile
	elif recv_data['type'] == "PROFILE":
		new_profile = recv_data['data']
		plantsettings = uheapq.heappop(heap)
		# Check if the new profile only contains all the valid fields, changes profile if true
		if set(plantsettings.keys()) == set(new_profile.keys()):
			plantsettings = new_profile
			uheapq.heappush(heap,new_profile)
			resp['data']['profile_resp'] = 'Profile has been changed to "%s"' % (plantsettings['Profile'])

		else:
			resp['data']['profile_resp'] = 'Could not change the plant profile'


	# Sending response back to the client
	timestamp = "%d-%d-%d_%d:%d:%d" % (time.localtime()[:6])
	resp['timestamp'] = timestamp
	client.sendData("response", resp)
    

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

# MQTTWrapper requires on_message to be defined first
client = MQTTWrapper.MQTTWrapper('192.168.0.10', 'EEERover', 'exhibition', on_message) # '192.168.1.4', 'PLUSNET-6QTFPK', '7dff6ec6df'

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

## Main Function!
if __name__ == "__main__":
	rtc.alarm(0,1000)
	state = next_print_state['Moisture']
	value = plantsettings[state]
	count = 0
	lcd.clear()
	lcd.move_to(0,0)
	lcd.putstr("%s: \n%s" %(state,value))
	shutdown = 0

	while not shutdown:
		# Asynchronous means the embed to can perform other things while listening
		client.listenAsync() 
		
		## Get new plantsettings from the heap
		plantsettings = heap[0]
		shutdown = plantsettings['Shutdown']
		## Performs this loop every second
		if rtc.alarm_left() <= 0:
			
			# Adds a new set of readings in the moving average buffers
			ALbuffer.update(alpsensor.getALReading())
			proxbuffer.update(alpsensor.getProxReading())
			tempbuffer.update(tempsensor.read())
			humidsensor.measure()
			humidbuffer.update(humidsensor.humidity())
			moistbuffer.update(moistsensor.read())

			# Changes LCD Display every 5 seconds
			# LCD only shows current readings, not the profile thresholds
			if count % 5 == 0:
				state = next_print_state[state]
				
				if state == 'Profile':
					value = plantsettings[state]
				elif state == 'Light':
					value = str(round(ALbuffer.getMA(),2)) + " lux"
				elif state == 'Temp':
					value = str(round(tempbuffer.getMA(),2)) + " degs"
				elif state == 'Humidity':
					value = str(round(humidbuffer.getMA(),2)) + "%"
				elif state == 'Moisture':
					value = str(round(moistbuffer.getMA(),2))


				lcd.clear()
				lcd.move_to(0,0)
				lcd.putstr("%s: \n%s" %(state,value))


			count += 1
			rtc.alarm(0,1000)

		## Control loop for Light
		lightlowthres = plantsettings['Light_low']
		if ALbuffer.getMA() < lightlowthres:
			new_duty = (lightlowthres - ALbuffer.getMA())/lightlowthres * 1024
			
			# Sends a notification that the lamp has been turned on
			if not warning_status['low_light']:
				warning_status['low_light'] = True
				
				timestamp = "%d-%d-%d_%d:%d:%d" % (time.localtime()[:6])
				action = {'timestamp' : timestamp, 'type' : 'ACTION' }
				action['data'] = "The plant is receiving too little light, turning on lamp"
				client.sendData("response", action)
		
		else:
			new_duty = 0	
			warning_status['low_light'] = False
		lightingcontroller.duty(int(new_duty))

		## Control loop for water level
		watersensor['vcc'].value(1)
		if watersensor['sense'].value() == 0 and not warning_status['low_water']:
				warning_status['low_water'] = True
				
				timestamp = "%d-%d-%d_%d:%d:%d" % (time.localtime()[:6])
				warning = {'timestamp' : timestamp, 'type' : 'WARNING' }
				warning['data'] = "Low water tank level, refill the water tank"
				client.sendData("response", warning)

		elif watersensor['sense'].value() == 1 and warning_status['low_water']:
				warning_status['low_water'] = False
				note = {'timestamp' : timestamp, 'type' : 'NOTIFICATION' }
				note['data'] = "Water tank has been refilled"
				client.sendData("response", note)

		watersensor['vcc'].value(0)


		## Control loop for "Pump" - servomotor
		moistlowthres = plantsettings['Moist_low']
		if moistbuffer.getMA() < moistlowthres and not warning_status['low_moist']:
			warning_status['low_moist'] = True
			pumpcontroller.duty(int(2./20*1024))

			note = {'timestamp' : timestamp, 'type' : 'NOTIFICATION' }
			note['data'] = "Plant is currently being watered"
			client.sendData("response", note)
		elif moistbuffer.getMA() >= moistlowthres and warning_status['low_moist']:
			warning_status['low_moist'] = False
			pumpcontroller.duty(int(1./20*1024))			