import vcnl4010 as Sensor
from umqtt.simple import MQTTClient
import network
import machine, time, json


# Interval Variables for embed, declared as global variables

led = machine.Pin(0, machine.Pin.OUT)
led.high()

rtc = machine.RTC()


# Callback function to process MQTT messages
def on_message(topic, msg):
    print("Received message '" + str(msg) + "' on topic '"
        + topic + "'")
    timestamp = msg.split("_")
    Y, M, D = [int(i) for i in timestamp[0].split("-")]
    h, m, s = [int(i) for i in timestamp[1].split(":")]
    rtc.init((Y,M,D,h,m,s))
    print("Clock initialized to " + str(rtc.now()))
# Custom MQTT Wrapper for our embed
class MQTTWrapper:
	def __init__(self):
		self.client = MQTTClient(machine.unique_id(), "192.168.0.10")
		# self.client.on_connect = on_connect
		# self.client.on_disconnect = on_disconnect
		self.client.on_message = on_message
		self.prefix = "esys/majulah/"

		# This stops other machines from connecting to us
		ap_if = network.WLAN(network.AP_IF)
		ap_if.active(False)

		# This allows us to connect to the router
		sta_if = network.WLAN(network.STA_IF)
		sta_if.active(True)
		sta_if.connect('EEERover','exhibition')  #'PLUSNET-6QTFPK','7dff6ec6df')#

		connected = False
		while not connected:
			try:
				self.client.connect()
				connected = True
				led.low()
			except OSError:
				# machine.reset()
				pass
			except IndexError:
				# machine.reset()
				pass

	def __del__(self):
		self.client.disconnect()

	def sendData(self, topic = "", data = ""):
		self.client.publish(self.prefix + topic, json.dumps(data).encode('utf-8'))

	def syncTime(self):
		self.client.subscribe(self.prefix + "timesync")
		self.client.wait_msg()

if __name__ == "__main__":
	i2c = machine.I2C(scl = machine.Pin(5), sda = machine.Pin(4), freq = 100000)
	sense = Sensor.ALPSensor(i2c)
	client = MQTTWrapper()
	client.syncTime()

	# timer = machine.RTC()
	# timer.alarm(0, 60000)

	# while timer.alarm_left() > 0:
	# 	timestamp = "%d-%d-%d_%d:%d:%d" % (time.localtime()[:6])
	# 	buff = {"timestamp" : timestamp, "ambient": sense.getALReading(), "prox" : sense.getRawProx()}
	# 	client.sendData('ambient', buff)
	# 	time.sleep(1)