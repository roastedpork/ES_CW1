from umqtt.simple import MQTTClient
import Constants as var #	Variables had to be written in another file due to mem allocation
import machine, time, json, dht
import MQTTWrapper
import network
import uheapq
import gc

# Enables garbage collection for heap
gc.enable()

# Runs garbage collection before allocation onto heap
gc.collect()
uheapq.heappush(var.heap, var.plantsettings)

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
				resp['data'][cmd] = var.read_func_map[cmd]()	
			except KeyError:
				pass

	# If msg is a request to set the embed clock
	elif recv_data['type'] == "SET_TIME":
		resp['data']['timesync'] = setTime(recv_data['timestamp'])
	
	# If msg is a request to set a certain control parameter
	elif recv_data['type'] == "SET":
		try:
			_type, _value = recv_data['data']
			_plantsettings = uheapq.heappop(var.heap)
			if _type in _plantsettings.keys():
				_plantsettings[_type] = _value
				resp['data']['set_resp'] = '"%s" parameter successfully changed to "%f"' % (_type,_value)
			else:
				resp['data']['set_resp'] = 'There is no "%s" control parameter' % (_type)
			
			uheapq.heappush(var.heap,_plantsettings)
		except ValueError:
			resp['data']['set_resp'] = 'Not enough values provided (This should not happen)'

	# If msg is a request to change the plant profile
	elif recv_data['type'] == "PROFILE":
		new_profile = recv_data['data']
		_plantsettings = uheapq.heappop(var.heap)
		# Check if the new profile only contains all the valid fields, changes profile if true
		if set(_plantsettings.keys()) == set(new_profile.keys()):
			_plantsettings = new_profile
			uheapq.heappush(var.heap,new_profile)
			resp['data']['profile_resp'] = 'Profile has been changed to "%s"' % (var.plantsettings['Profile'])

		else:
			resp['data']['profile_resp'] = 'Could not change the plant profile'


	# Sending response back to the client
	timestamp = "%d-%d-%d_%d:%d:%d" % (time.localtime()[:6])
	resp['timestamp'] = timestamp
	client.sendData("response", resp)
    
# MQTTWrapper requires on_message to be defined first
client = MQTTWrapper.MQTTWrapper('192.168.0.10', 'EEERover', 'exhibition', on_message) # '192.168.1.4', 'PLUSNET-6QTFPK', '7dff6ec6df'

def send_msg(_type, _str):
	timestamp = "%d-%d-%d_%d:%d:%d" % (time.localtime()[:6])
	msg = {'timestamp' : timestamp, 'type' : _type }
	msg['data'] = _str
	client.sendData("response", msg)

## Main Function!
if __name__ == "__main__":
	var.rtc.alarm(0,1000)
	state = var.next_print_state['Moisture']
	value = var.plantsettings[state]
	count = 0
	var.lcd.clear()
	var.lcd.move_to(0,0)
	var.lcd.putstr("%s: \n%s" %(state,value))
	shutdown = 0

	while not shutdown:
		# Asynchronous means the embed to can perform other things while listening
		client.listenAsync() 
		
		## Get new var.plantsettings from the heap
		var.plantsettings = var.heap[0]
		shutdown = var.plantsettings['Shutdown']
		## Performs this loop every second
		if var.rtc.alarm_left() <= 0:
			
			# Adds a new set of readings in the moving average buffers
			var.ALbuffer.update(var.alpsensor.getALReading())
			var.proxbuffer.update(var.alpsensor.getProxReading())
			var.tempbuffer.update(var.tempsensor.read())
			var.humidsensor.measure()
			var.humidbuffer.update(var.humidsensor.humidity())
			var.moistbuffer.update(var.moistsensor.read())

			# Changes LCD Display every 5 seconds
			# LCD only shows current readings, not the profile thresholds
			if count % 5 == 0:
				state = var.next_print_state[state]
				
				if state == 'Profile':
					value = var.plantsettings[state]
				elif state == 'Light':
					value = str(round(var.ALbuffer.getMA(),2)) + " lux"
				elif state == 'Temp':
					value = str(round(var.tempbuffer.getMA(),2)) + " degs"
				elif state == 'Humidity':
					value = str(round(var.humidbuffer.getMA(),2)) + "%"
				elif state == 'Moisture':
					value = str(round(var.moistbuffer.getMA(),2))

				var.lcd.clear()
				var.lcd.move_to(0,0)
				var.lcd.putstr("%s: \n%s" %(state,value))

			count += 1
			var.rtc.alarm(0,1000)

		## Control loop for Light
		lightlowthres = var.plantsettings['Light_low']
		if var.ALbuffer.getMA() < lightlowthres:
			new_duty = (lightlowthres - var.ALbuffer.getMA())/lightlowthres * 1024
			
			# Sends a notification that the lamp has been turned on
			if not var.warning_status['low_light']:
				var.warning_status['low_light'] = True

				send_msg('ACTION',"The plant is receiving too little light, turning on lamp")
		else:
			new_duty = 0	
			var.warning_status['low_light'] = False
		var.lightingcontroller.duty(int(new_duty))

		## Control loop for water level
		var.watersensor['vcc'].value(1)
		if var.watersensor['sense'].value() == 0 and not var.warning_status['low_water']:
				var.warning_status['low_water'] = True
				send_msg('WARNING',"Low water tank level, refill the water tank")
				
		elif var.watersensor['sense'].value() == 1 and var.warning_status['low_water']:
				var.warning_status['low_water'] = False
				send_msg('NOTIFICATION',"Water tank has been refilled")

		var.watersensor['vcc'].value(0)


		## Control loop for "Pump" - servomotor
		moistlowthres = var.plantsettings['Moisture_low']
		if var.moistbuffer.getMA() < moistlowthres and not var.warning_status['low_moist']:
			var.warning_status['low_moist'] = True
			var.pumpcontroller.duty(int(2./20*1024))
			send_msg('ACTION',"Plant is too dry, water pump activated")

		elif var.moistbuffer.getMA() >= moistlowthres and var.warning_status['low_moist']:
			var.warning_status['low_moist'] = False
			var.pumpcontroller.duty(int(1./20*1024))
			send_msg('NOTIFICATION',"Plant has been watered")

	send_msg('SHUTDOWN_RESPONSE', "Greenhouse system deactivated")