from umqtt.simple import MQTTClient
import network
import machine, time, json

class MQTTWrapper:
	def __init__(self):
		self.client = MQTTClient(machine.unique_id(), "192.168.0.10") #"192.168.1.15") #
		self.client.set_callback(on_message)
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
				machine.reset()
				pass
			except IndexError:
				machine.reset()
				pass

	def __del__(self):
		self.client.disconnect()

	def sendData(self, topic = "", data = ""):
		self.client.publish(self.prefix + topic, json.dumps(data).encode('utf-8'))

	# Blocking implementation of the listening loop
	def listenSync(self):
		self.client.subscribe(self.prefix + 'command')
		self.wait_msg()

	# Non-blocking implementation of the listening loop
	def listenAsync(self):
		self.client.subscribe(self.prefix + 'command')
		self.check_msg()