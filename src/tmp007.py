import machine
import time
class TempSensor:
	def __init__(self, id, i2c_handler):
		self.ID = id
		self.i2c = i2c_handler

		self.REG_TDIE = 0x01

	def read(self):
		combined = self.i2c.readfrom_mem(self.ID, self.REG_TDIE,2)
		reading = bytearray(combined)

		temp = ((reading[0] << 8) | reading[1])
		
		# Handling 14-bit signed integer value
		if temp & 0x8000:
			temp = ((0x10000 - temp) >> 2) * -1
		else:
			temp >>= 2

		return temp*0.03125


def main():
	i2c = machine.I2C(scl = machine.Pin(5), sda = machine.Pin(4), freq = 100000)
	sensor = TempSensor(0x40, i2c)

	for i in range(10):
		print("%.2f degrees Celcius" % (sensor.read()))
		time.sleep(1)

if __name__ == "__main__":
	main()
