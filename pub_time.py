import paho.mqtt.client as mqtt
import datetime, time


def on_connect(client, userdata, flags, rc):
		print("Connection returned result: " + str(rc))

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")

client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect

client.connect('192.168.0.10')
# client.subscribe('esys/majulah/ambient')
client.loop_start()

while 1:
	# client.loop()	

	stamp = datetime.datetime.now().isoformat("_")
	client.publish('esys/majulah/timesync', stamp.encode('utf-8'))
	time.sleep(1)