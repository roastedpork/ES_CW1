import machine, dht

d = dht.DHT11(machine.Pin(13))

d.measure()

print("humidity :", d.humidity())