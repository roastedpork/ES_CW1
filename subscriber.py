import paho.mqtt.client as mqtt
import json, csv, os

def on_connect(client, userdata, flags, rc):
		print("Connection returned result: " + str(rc))#connack_string(rc))

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")

def on_message(client, userdata, message):
	print("Received message '" + str(message.payload) + "' on topic '"
	    + message.topic + "' with QoS " + str(message.qos))
	cnvt = json.loads(message.payload)

	if "log.csv" not in os.listdir(".."):
		with open("log.csv", "wb") as csvfile:
			fieldnames = cnvt.keys()
			writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
			writer.writeheader()
			writer.writerow(cnvt)
	else:
		print("appending")
		with open("log.csv", "ab") as csvfile:
			fieldnames = cnvt.keys()
			writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
			writer.writerow(cnvt)

client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

client.connect('192.168.0.10')
client.subscribe('esys/majulah/ambient') #timesync') #
# client.loop_start()

while 1:
	client.loop()	