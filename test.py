import vcnl4010 as Sensor
import machine

i2c = machine.I2C(scl = machine.Pin(5), sda = machine.Pin(4), freq = 100000)
sense = Sensor.ALPSensor(i2c)
print(sense.getRawLight())