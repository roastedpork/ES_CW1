import vcnl4010 as Sensor
from umqtt.simple import MQTTClient
import network
import machine

class MQTTWrapper:
	def __init__(self):
		self.client = MQTTClient(machine.unique_id(), "192.168.0.10")
		self.prefix = "esys/majulah/"

	def sendData(self, topic = "", data = ""):
		self.client.publish(self.prefix + topic, bytes(data, 'utf-8'))


if __name__ == "__main__":
	i2c = machine.I2C(scl = machine.Pin(5), sda = machine.Pin(4), freq = 100000)
	sense = Sensor.ALPSensor(i2c)
	client = MQTTWrapper()


	# This stops other machines from connecting to us
	ap_if = network.WLAN(network.AP_IF)
	ap_if.active(False)

	# This allows us to connect to the router
	sta_if = network.WLAN(network.STA_IF)
	sta_if.connect('EEERover','exhibition')

	