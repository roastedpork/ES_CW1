import vcnl4010 as Sensor
from umqtt.simple import MQTTClient
import network
import machine, time

def on_connect(client, userdata, flags, rc):
		print("Connection returned result: " + str(rc))#connack_string(rc))

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")

class MQTTWrapper:
	def __init__(self):
		self.client = MQTTClient(machine.unique_id(), "192.168.0.10")
		self.client.on_connect = on_connect
		self.client.on_disconnect = on_disconnect
		self.prefix = "esys/majulah/"
		self.client.connect()
		
	def __del__(self):
		self.client.disconnect()

	def sendData(self, topic = "", data = ""):
		self.client.publish(self.prefix + topic, str(data).encode('utf-8'))


if __name__ == "__main__":
	i2c = machine.I2C(scl = machine.Pin(5), sda = machine.Pin(4), freq = 100000)
	sense = Sensor.ALPSensor(i2c)


	# This stops other machines from connecting to us
	ap_if = network.WLAN(network.AP_IF)
	ap_if.active(False)

	# This allows us to connect to the router
	sta_if = network.WLAN(network.STA_IF)
	sta_if.active(True)
	sta_if.connect('EEERover','exhibition')

	
	client = MQTTWrapper()

	for i in range(10):
		client.sendData('ambient', sense.getALReading())
		time.sleep(1)