import vcnl4010 as Sensor
from umqtt.simple import MQTTClient
import network
import machine, time, json

led = machine.Pin(0, machine.Pin.OUT)
led.high()

def on_connect(client, userdata, flags, rc):
		print("Connection returned result: " + str(rc))
		led.low()

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")
        led.high()

def on_message(client, userdata, message):
    print("Received message '" + str(message.payload) + "' on topic '"
        + message.topic + "' with QoS " + str(message.qos))


class MQTTWrapper:
	def __init__(self):
		self.client = MQTTClient(machine.unique_id(), "192.168.0.10")
		self.client.on_connect = on_connect
		self.client.on_disconnect = on_disconnect
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

	def syncTime():
		self.client.subscribe(self.prefix + "timesync")


if __name__ == "__main__":
	i2c = machine.I2C(scl = machine.Pin(5), sda = machine.Pin(4), freq = 100000)
	sense = Sensor.ALPSensor(i2c)
	client = MQTTWrapper()


	for i in range(10):
		timestamp = "%d-%d-%d_%d:%d:%d" % (time.localtime()[:6])
		data = {"ambient": sense.getALReading(), "prox" : sense.getRawProx()}
		buff = {"timestamp" : timestamp, "data" : data}
		client.sendData('ambient', buff)
		time.sleep(1)