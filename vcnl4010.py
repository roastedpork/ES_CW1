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
		self.LIGHT_ADD = 0x85		# 0x85 and 0x86 are MSB and LSB of light reading, big endian 	
		self.PROX_ADD = 0x87		# 0x87 and 0x88 are MSB and LSB of proximity reading, big endian

		self.sensor.writeto_mem(self.ID, self.PROX_CONFIG, str(0x00).encode())
		self.sensor.writeto_mem(self.ID, self.LIGHT_CONFIG, str(0x9D).encode())

	def takeReading(self):
		buf = str(0xff).encode()
		self.sensor.writeto_mem(self.ID, self.CMD_REG, buf)

	def getRawLight(self):
		self.takeReading()

		combined = self.sensor.readfrom_mem(self.ID, self.LIGHT_ADD,2)
		hi, lo = bytearray(combined)
		hi <<= 8
		return hi + lo

	def getRawProx(self):
		self.takeReading()

		combined = self.sensor.readfrom_mem(self.ID, self.PROX_ADD,2)
		hi, lo = bytearray(combined)
		hi <<= 8
		return hi + lo

def main():
	sensor = Sensor()
	readout = sensor.getRawLight()
	print("Light sensor raw data reading:", readout)
	readout = sensor.getRawProx()
	print("Proximity sensor raw data reading:",readout)

if __name__ == "__main__":
	main()