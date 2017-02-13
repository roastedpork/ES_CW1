from umqtt.simple import MQTTClient
import network
import machine, time, json

led = machine.Pin(0, machine.Pin.OUT)
led.high()

# MQTT wrapper class
class MQTTWrapper:
	def __init__(self, _broker_ip, _ssid, _pw, _f):
		self.client = MQTTClient(machine.unique_id(), _broker_ip) 
		self.prefix = "esys/majulah/"
		self.client.set_callback(_f)

		# This stops other machines from connecting to us
		ap_if = network.WLAN(network.AP_IF)
		ap_if.active(False)

		# This allows us to connect to the router
		sta_if = network.WLAN(network.STA_IF)
		sta_if.active(True)
		sta_if.connect(_ssid, _pw)
		led.low()
		connected = False
		while not connected:
			try:
				self.client.connect()
				connected = True
				led.low()
			except OSError:
				machine.reset()

			except IndexError:
				machine.reset()


		self.client.subscribe(self.prefix + 'command')

	def __del__(self):
		self.client.disconnect()

	def sendData(self, topic = "", data = ""):
		self.client.publish(self.prefix + topic, json.dumps(data).encode('utf-8'))
		self.client.subscribe(self.prefix + 'command')

	# Blocking implementation of the listening loop
	def listenSync(self):
		self.client.wait_msg()

	# Non-blocking implementation of the listening loop
	def listenAsync(self):
		self.client.check_msg()

	def setCallback(f):
		self.client.set_callback(_f)

if __name__ == "__main__":
	pass