import vcnl4010 as ALPSensor
import tmp007 as TempSensor
import MQTTWrapper
from umqtt.simple import MQTTClient
import network
import machine, time, json


# Interval Variables for embed, declared as global variables
led = machine.Pin(0, machine.Pin.OUT)
led.high()

i2c = machine.I2C(scl = machine.Pin(5), sda = machine.Pin(4), freq = 100000)
alpsensor = ALPSensor.ALPSensor(i2c)
tempsensor = TempSensor.TempSensor(0x40, i2c)
rtc = machine.RTC()

client = MQTTWrapper('192.168.0.10', 'EEERover', 'exhibition') #'192.168.1.15', 'PLUSNET-6QTFPK', '7dff6ec6df')
client.setCallback(on_message)

# Callback function to sync RTC via MQTT message
def on_message(topic, msg):
    # Process command based on message arguments
	recv_data = json.loads(str(msg,'utf-8'))
	resp = {}

	if type(recv_data['command']) is list:
		for cmd in recv_data['command']:
			try:
				if cmd == 'timesync':
					resp[cmd] = cmd_func_map[cmd](recv_data['timestamp'])
				else:
					resp[cmd] = cmd_func_map[cmd](	)

			except KeyError:
				pass

	# Sending response back to the client
	timestamp = "%d-%d-%d_%d:%d:%d" % (time.localtime()[:6])
	resp['timestamp'] = timestamp
	client.sendData("response", resp)
    

# Specialized callback functions based on command given by client
def cmd_ambient():
	return alpsensor.getALReading()

def cmd_timesync(_timestamp):
	timestamp = _timestamp.split("_")
	Y, M, D = [int(i) for i in timestamp[0].split("-")]
	h, m, s = [int(i) for i in timestamp[1].split(".")[0].split(":")]
	rtc.datetime((Y,M,D,0,h,m,s,0))
	return "Success"

def cmd_prox():
	return alpsensor.getProxReading()

def cmd_temp():
	return tempsensor.read()

# Mapping function for the different types of commands
cmd_func_map = 	{
				'ambient' : cmd_ambient,
				'timesync' : cmd_timesync,
				'prox' : cmd_prox,
				'temp' : cmd_temp,
				}

# # MQTT wrapper class
# class MQTTWrapper:
# 	def __init__(self, _broker_ip, _ssid, _pw):
# 		self.client = MQTTClient(machine.unique_id(), _broker_ip) 
# 		self.prefix = "esys/majulah/"

# 		# This stops other machines from connecting to us
# 		ap_if = network.WLAN(network.AP_IF)
# 		ap_if.active(False)

# 		# This allows us to connect to the router
# 		sta_if = network.WLAN(network.STA_IF)
# 		sta_if.active(True)
# 		sta_if.connect(_ssid, _pw)

# 		connected = False
# 		while not connected:
# 			try:
# 				self.client.connect()
# 				connected = True
# 				led.low()
# 			except OSError:
# 				machine.reset()

# 			except IndexError:
# 				machine.reset()


# 		self.client.subscribe(self.prefix + 'command')

# 	def __del__(self):
# 		self.client.disconnect()

# 	def sendData(self, topic = "", data = ""):
# 		self.client.publish(self.prefix + topic, json.dumps(data).encode('utf-8'))
# 		self.client.subscribe(self.prefix + 'command')

# 	# Blocking implementation of the listening loop
# 	def listenSync(self):
# 		self.client.wait_msg()

# 	# Non-blocking implementation of the listening loop
# 	def listenAsync(self):
# 		self.client.check_msg()

# 	def setCallback(f):
# 		self.client.set_callback(f)

if __name__ == "__main__":

	while 1:
		client.listenAsync() # Asynchronous means the embed to can perform other things while listening