import machine
class Sensor:
	def __init__(self):
		self.ID = 0x13
		self.sensor = machine.I2C(scl = machine.Pin(5), sda = machine.Pin(4), freq = 100000)

		self.CMD_REG = 0x80
		self.LIGHT_ADD_HI = 0x85
		self.LIGHT_ADD_LO = 0x86

		self.PROX_ADD_HI = 0x87
		self.PROX_ADD_LO = 0x88

	def takeReading(self):
		buf = str(0xff).encode()
		self.sensor.writeto_mem(self.ID, self.CMD_REG, buf)

	def getRawLight(self):
		self.takeReading()
		hi = self.sensor.readfrom_mem(self.ID, self.LIGHT_ADD_HI,1)
		lo = self.sensor.readfrom_mem(self.ID, self.LIGHT_ADD_LO,1)
		hi , lo = bytearray(hi)[0], bytearray(lo)[0]
		hi <<= 8
		return hi + lo

	def getRawProx(self):
		self.takeReading()
		hi = self.sensor.readfrom_mem(self.ID, self.PROX_ADD_HI,1)
		lo = self.sensor.readfrom_mem(self.ID, self.PROX_ADD_LO,1)
		hi , lo = bytearray(hi)[0], bytearray(lo)[0]
		hi <<= 8
		return hi + lo

def main():
	sensor = Sensor()
	readout = sensor.getRawLight()

	print(readout)
	readout = sensor.getRawProx()

	print(readout)

if __name__ == "__main__":
	main()