import machine
import time
class Sensor:
	def __init__(self):
		self.ID = 0x13
		self.sensor = machine.I2C(scl = machine.Pin(5), sda = machine.Pin(4), freq = 100000)

		self.CMD_REG = 0x80			# Measurement enable bits
		self.PROX_CONFIG = 0x82		# Rate of proximity measurement
		self.LED_CONFIG = 0x83 		# LED used to measure proximity 
		self.LIGHT_CONFIG = 0x84	# Ambient light measurement parameters
		self.DATA_ADD = 0x85
		# self.LIGHT_ADD = 0x85		# 0x85 and 0x86 are MSB and LSB of light reading, big endian 	
		# self.PROX_ADD = 0x87		# 0x87 and 0x88 are MSB and LSB of proximity reading, big endian
		self.IRQ_CTRL = 0x89
		self.sensor.writeto_mem(self.ID, self.PROX_CONFIG, str(0x00).encode())
		self.sensor.writeto_mem(self.ID, self.LIGHT_CONFIG, str(0x9D).encode())
		self.sensor.writeto_mem(self.ID, self.IRQ_CTRL, str(0x02).encode())

		self.reading = None

		self.first_read = True

	def read(self):
		buf = str(0xff).encode()
		self.sensor.writeto_mem(self.ID, self.CMD_REG, buf)

		if self.first_read:
			time.sleep_us(1470)
			self.first_read = False

		combined = self.sensor.readfrom_mem(self.ID, self.DATA_ADD,4)
		self.reading = bytearray(combined)

	def getRawLight(self):
		self.read()
		hi, lo = self.reading[0], self.reading[1]
		hi <<= 8
		return hi + lo

	def getRawProx(self):
		self.read()
		hi, lo = self.reading[2], self.reading[3]
		hi <<= 8
		return hi + lo

	def getALS():
		return self.getRawLight * 0.25

def main():
	sensor = Sensor()
	readout = sensor.getRawLight()
	print("Light sensor raw data reading:", readout)
	readout = sensor.getALS()
	print("Light sensor reading: %f lux" % (readout))
	readout = sensor.getRawProx()
	print("Proximity sensor raw data reading:",readout)

if __name__ == "__main__":
	main()