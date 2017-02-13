"""Implements a HD44780 character LCD connected via PCF8574 on I2C.
   This was tested with: https://www.wemos.cc/product/d1-mini.html"""

from time import sleep_ms, ticks_ms
from machine import I2C, Pin
from esp8266_i2c_lcd import I2cLcd

# The PCF8574 has a jumper selectable address: 0x20 - 0x27
DEFAULT_I2C_ADDR = 0x27

def test_main():
	"""Test function for verifying basic functionality."""
	print("Running test_main")
	i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)
	lcd = I2cLcd(i2c, DEFAULT_I2C_ADDR, 2, 16)
	lcd.putstr("It Works!\nSecond Line")
	sleep_ms(3000)
	lcd.clear()
	count = 0
	while True:
		lcd.clear()
		lcd.move_to(0, 0)
		lcd.putstr("BL off")
		lcd.backlight_off()    
		sleep_ms(2000)

		lcd.clear()
		lcd.move_to(0, 0)
		lcd.putstr("BL on")
		lcd.backlight_on()    
		sleep_ms(2000)

		lcd.clear()
		lcd.move_to(0, 0)
		lcd.putstr("DISP off")
		lcd.display_off()    
		sleep_ms(2000)

		lcd.clear()
		lcd.move_to(0, 0)
		lcd.putstr("DISP on")
		lcd.display_on()    
		sleep_ms(2000)

		lcd.clear()
		lcd.move_to(0, 0)
		lcd.putstr("BL & DISP off")
		lcd.backlight_off()
		lcd.display_off()
		sleep_ms(2000)

		lcd.clear()
		lcd.move_to(0, 0)
		lcd.putstr("BL & DISP on")
		lcd.backlight_on()
		lcd.display_on()
		sleep_ms(2000)

		lcd.clear()
		lcd.move_to(0, 0)
		lcd.putstr("BL off\nDISP on")
		lcd.backlight_off()
		lcd.display_on()
		sleep_ms(2000)

		lcd.clear()
		lcd.move_to(0, 0)
		lcd.putstr("BL on \n DISP off")
		lcd.backlight_on()
		lcd.display_off()
		sleep_ms(2000)		

if __name__ == "__main__":
	test_main()
