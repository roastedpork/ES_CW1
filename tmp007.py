import machine
import time
class TempSensor:
	def __init__(self, i2c_handler):
		self.ID = 0x40
		self.i2c = i2c_handler

		self.REG_VSENSOR = 0x00
		self.REG_TDIE = 0x01
		self.REG_CONFIG = 0x02

		self.reading = None

	def readRawVoltage(self):
		combined = self.i2c.readfrom_mem(self.ID, self.REG_VSENSOR,2)
		self.reading = bytearray(combined)

	def readRawTDie(self):
		combined = self.i2c.readfrom_mem(self.ID, self.REG_TDIE,2)
		self.reading = bytearray(combined)

def main():
	i2c = machine.I2C(scl = machine.Pin(5), sda = machine.Pin(4), freq = 100000)
	sensor = TempSensor(i2c)

	r1 = bytearray(i2c.readfrom_mem(0x40, 0x00, 2))
	r2 = bytearray(i2c.readfrom_mem(0x40, 0x01, 2))

	print(r1)
	print(r1[0],r1[1])
	print(r2)
	print(r2[0],r2[1])

if __name__ == "__main__":
	main()
