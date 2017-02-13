import paho.mqtt.client as mqtt
import json, csv, os, sys, datetime, time, re


# Callback function to indicate a successful connection
def on_connect(client, userdata, flags, rc):
	if rc == 0:
		print("Successfully connected to broker")

# Callback function to handle messages from embed server
def on_message(client, userdata, message):
	response = json.loads(message.payload)

	if response['type'] == 'READ_RESPONSE':
		print("Current readings from the greenhouse")
		for k,v in sorted(response['data'].items()):
			print("%s: %.2f" * (k,v)) 
		print("")

	elif response['type'] == 'SET_RESPONSE':
		print(response['data']['set_resp'])
		print("")

	elif response['type'] == 'SET_TIME_RESPONSE':
		print(response['data']['timesync'])
		print("")

	elif response['type'] == 'PROFILE_RESPONSE':
		print(response['data']['profile_resp'])
		print("")

	elif response['type'] == 'WARNING':
		pass

	elif response['type'] == 'ACTION':
		pass

	recv = True

# Setting up client-side MQTT handler
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(sys.argv[1])
recv = False

# Set of plant profiles available 
profiles = 	[
			{ 'Profile' : 'basil', 'Light' : 1000, 'Temperature', 25, 'Humidity' : 75, 'Moisture' : 50},
			{ 'Profile' : 'lavender', 'Light' : 700, 'Temperature', 20, 'Humidity' : 50, 'Moisture' : 72},
			]



# Polling loop for user input
while 1:
	print("Enter command:")
	cmd_in = raw_input().lower()
	sent = True
	recv = False
	timestamp = datetime.datetime.now().isoformat("_")

	# If user wants to read certain values from the greenhouse
	if cmd_in[:4] == "read":
		cmds = cmd_in[5:].split(" ")
		print("")

		data = {"timestamp": timestamp, 'type': 'READ', "data" : cmds}
		print(data)
		client.publish('esys/majulah/command', json.dumps(data).encode('utf-8'))
	
	# If user wants to change the plant profile
	elif cmd_in[:11] == "set profile":
		_plant = cmd_in[12:].lower()
		new_profile = None
		for prof in profiles:
			if prof['Profile'] == _plant:
				new_profile = prof
				break

		# Sends new profile if programme receives a valid plant from the user
		if new_profile is not None:
			data = {"timestamp": timestamp, 'type': 'PROFILE', 'data' : new_profile}
			print(data)
			client.publish('esys/majulah/command', json.dumps(data).encode('utf-8'))

		# Else prompts an error message
		else:
			sent = False
			print("This plant setting is currently unavailable")

	# If user wants to set the time on the embed
	elif cmd_in == "set time":
		data = {"timestamp": timestamp, 'type': 'SET_TIME'}
		print(data)
		client.publish('esys/majulah/command', json.dumps(data).encode('utf-8'))

	# If user wants to set a specific target parameter for the greenhouse to maintain
	elif cmd_in[:3] == "set":
		regex = re.search('set (\w+) (\d+[\.[\d]+]?)', cmd_in)
		try:
			_type, _value = regex.groups()
			data = {"timestamp": timestamp, 'type': 'SET', 'data' : (_type, float(_value))}
			print(data)
			client.publish('esys/majulah/command', json.dumps(data).encode('utf-8'))

		except ValueError:
			sent = False
			print("Please enter a float value")

	# If user wants to end the client
	elif cmd_in == "end":
		break

	if sent:
		client.loop_start()	
		client.subscribe('esys/majulah/response') 
		while not recv:
			pass
		client.loop_stop()
