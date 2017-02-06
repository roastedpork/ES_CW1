import machine
import time
class ALPSensor:
	def __init__(self, i2c_handler):
		self.ID = 0x13
		self.i2c = i2c_handler

		self.CMD_REG = 0x80			# Measurement enable bits
		self.PROX_CONFIG = 0x82		# Rate of proximity measurement
		self.LED_CONFIG = 0x83 		# LED used to measure proximity 
		self.LIGHT_CONFIG = 0x84	# Ambient light measurement parameters
		self.DATA_ADD = 0x85
		# self.LIGHT_ADD = 0x85		# 0x85 and 0x86 are MSB and LSB of light reading, big endian 	
		# self.PROX_ADD = 0x87		# 0x87 and 0x88 are MSB and LSB of proximity reading, big endian
		self.IRQ_CTRL = 0x89
		self.i2c.writeto_mem(self.ID, self.CMD_REG, str(0x07).encode())
		self.i2c.writeto_mem(self.ID, self.PROX_CONFIG, str(0x07).encode())
		self.i2c.writeto_mem(self.ID, self.LED_CONFIG, str(0x0A).encode())
		self.i2c.writeto_mem(self.ID, self.LIGHT_CONFIG, str(0x9D).encode())
		self.i2c.writeto_mem(self.ID, self.IRQ_CTRL, str(0x02).encode())


		self.PROX_INF = 2098.0 # default value
		self.PROX_UPPER = 200
		self.PROX_LOWER = 1
		self.reading = None

		self.first_read = True

	def read(self):
		
		if self.first_read:
			time.sleep_us(1470)
			self.first_read = False

		combined = self.i2c.readfrom_mem(self.ID, self.DATA_ADD,4)
		self.reading = bytearray(combined)

	def calibrate(self,_n):
		readouts = [self.getRawProx() for i in range(_n)]
		print(readouts)
		self.PROX_INF = float(sum(readouts))/len(readouts)

	def getRawLight(self):
		self.read()
		hi, lo = self.reading[0:2]
		hi <<= 8
		return hi + lo

	def getRawProx(self):
		self.read()
		hi, lo = self.reading[2:4]
		hi <<= 8
		return hi + lo

	def getALReading(self):
		return self.getRawLight() * 0.25

	def getProxReading(self):
		readout =  self.getRawProx() - self.PROX_INF

		return readout
def main():
	i2c = machine.I2C(scl = machine.Pin(5), sda = machine.Pin(4), freq = 100000)
	sensor = ALPSensor(i2c)
	# sensor.calibrate(1000)

	led = machine.Pin(0, machine.Pin.OUT)
	# led.low()
	# time.sleep(10)
	# led.high()

	readout = sensor.getRawLight()
	print("Light sensor raw data reading:", readout)
	readout = sensor.getALReading()
	print("Light sensor reading: %f lux" % (readout))
	readout = sensor.getRawProx()
	print("Proximity sensor raw data reading:", readout)
	readout = sensor.getProxReading()
	print("Proximity sensor reading: %f mm" % (readout))

	timer = machine.RTC()
	timer.alarm(0,60000)

	while timer.alarm_left() > 0:
		readout = sensor.getRawProx()
		if readout > 3000:
			led.low()
		else:
			led.high()

if __name__ == "__main__":
	main()
