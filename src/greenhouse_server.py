import vcnl4010 as ALPSensor
import tmp007 as TempSensor
import MQTTWrapper
from umqtt.simple import MQTTClient
import network
import machine, time, json, dht
from esp8266_i2c_lcd import I2cLcd


# Interval Variables for embed, declared as global variables
i2c = machine.I2C(scl = machine.Pin(5), sda = machine.Pin(4), freq = 100000)
alpsensor = ALPSensor.ALPSensor(i2c)
tempsensor = TempSensor.TempSensor(0x40, i2c)
humidsensor = dht.DHT11(machine.Pin(13))
rtc = machine.RTC()
rtc1 = machine.RTC()
lcd = I2cLcd(i2c, 0x27, 2, 16)

# Buffer class to implement a moving average filter for the input data
# implements a FIFO queue for the inputs
class Buffer:
	def __init__(self, _period = 10):
		self.buffer = [0.0 for i in range(_period)]

	def getMA(self):
		return sum(self.buffer)/len(self.buffer)

	def update(self, _input):
		self.buffer = [_input] +self.buffer[:-1]

	def changeMAPeriod(self, _period):
		if _period < len(self.buffer):
			self.buffer = self.buffer[:_period]
		elif _period > len(self.buffer):
			self.buffer += [0 for i in range(_period - len(self.buffer))]

AL_buffer = Buffer()
prox_buffer = Buffer()
temp_buffer = Buffer()
humid_buffer = Buffer()

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
					resp[cmd] = cmd_func_map[cmd]()

			except KeyError:
				pass

	# Sending response back to the client
	timestamp = "%d-%d-%d_%d:%d:%d" % (time.localtime()[:6])
	resp['timestamp'] = timestamp
	client.sendData("response", resp)
    

# Specialized callback functions based on command given by client
def cmd_timesync(_timestamp):
	timestamp = _timestamp.split("_")
	Y, M, D = [int(i) for i in timestamp[0].split("-")]
	h, m, s = [int(i) for i in timestamp[1].split(".")[0].split(":")]
	rtc.datetime((Y,M,D,0,h,m,s,0))
	return "Success"

def cmd_ambient():
	return AL_buffer.getMA()

def cmd_prox():
	return prox_buffer.getMA()

def cmd_temp():
	return temp_buffer.getMA()

def cmd_humidity():
	return humid_buffer.getMA()


# Mapping function for the different types of commands
cmd_func_map = 	{
				'ambient' : cmd_ambient,
				'timesync' : cmd_timesync,
				'prox' : cmd_prox,
				'temp' : cmd_temp,
				'humid' : cmd_humidity,
				}

client = MQTTWrapper.MQTTWrapper('192.168.1.15', 'PLUSNET-6QTFPK', '7dff6ec6df', on_message) #'192.168.0.10', 'EEERover', 'exhibition') #


# Implementing printing state FSM
next_print_state = 	{
					'Profile' : 'Light',
					'Light' : 'Temperature',
					'Temperature' : 'Humidity',
					'Humidity' : "Profile",
					}



if __name__ == "__main__":
	rtc.alarm(0,1000)
	state, value = next_print_state['Humidity']
	while 1:
		client.listenAsync() # Asynchronous means the embed to can perform other things while listening
		



		# # Adds readings into buffers every 1 second
		if rtc.alarm_left() <= 0:
			AL_buffer.update(alpsensor.getALReading())
			prox_buffer.update(alpsensor.getProxReading())
			temp_buffer.update(tempsensor.read())
			humidsensor.measure()
			humid_buffer.update(humidsensor.humidity())

			state = next_print_state[state]
			
			if state == 'Profile':
				value = 'Basil'
			elif state == 'Light':
				value = str(round(AL_buffer.getMA(),2))
			elif state == 'Temperature':
				value = str(round(temp_buffer.getMA(),2))
			elif state == 'Humidity':
				value = str(round(humid_buffer.getMA(),2))

			lcd.clear()
			lcd.move_to(0,0)
			lcd.putstr("%s: \n%s" %(state,value))

			rtc.alarm(0,1000)

