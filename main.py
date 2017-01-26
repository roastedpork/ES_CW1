from machine import Pin, I2C
import time

def main():
	led = Pin(0,Pin.OUT)
	for i in range(10):
		led.high()
		time.sleep(1.0)
		led.low()
		time.sleep(1.0)


if __name__ == "__main__":
	main()