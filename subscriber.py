import paho.mqtt.client as mqtt
import json, csv, os, sys

def on_connect(client, userdata, flags, rc):
		print("Connection returned result: " + str(rc))#connack_string(rc))

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")

def on_message(client, userdata, message):
	print("Received message '" + str(message.payload) + "' on topic '"
	    + message.topic + "' with QoS " + str(message.qos))
	
	if message.topic == "esys/majulah/ambient":
		cnvt = json.loads(message.payload)
		if "log.csv" not in os.listdir("."):
			with open("log.csv", "wb") as csvfile:
				writer = csv.DictWriter(csvfile, fieldnames = cnvt.keys())
				writer.writeheader()
				writer.writerow(cnvt)
		else:
			with open("log.csv", "ab") as csvfile:
				writer = csv.DictWriter(csvfile, fieldnames = cnvt.keys())
				writer.writerow(cnvt)

client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

topics = [('esys/majulah/ambient',0), ('esys/majulah/timesync',0)]

client.connect(sys.argv[1])
client.subscribe('esys/majulah/' + sys.argv[2]) 

while 1:
	client.loop()	