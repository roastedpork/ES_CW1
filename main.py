from machine import Pin, I2C
import vcnl4010
import time

def main():
	sensor = vcnl4010.Sensor()
	sensor.takeReading()
	readout = sensor.getRawLight()

	with open("test.txt",'w') as file:
		file.write(readout)

if __name__ == "__main__":
	main()