import machine
import time

class LCD:
	def __init__(self, id, i2c_handler):
		self.ID = 0x27
		self.i2c = i2c_handler

		# Commands
		self.CMD_CLEARDISP = 0x01
		self.CMD_RETURNHOME = 0x02
		self.CMD_ENTRYMODESET = 0x04
		self.CMD_DISPCNTR = 0x08
		self.CMD_CURSORSHIFT = 0x10
		self.CMD_FUNCSET = 0x20
		self.CMD_SETCGRAMADDR = 0x40
		self.CMD_SETDDRAMADDR = 0x80

		# Flags for display entry mode
		self.ENTRYRIGHT = 0x00
		self.ENTRYLEFT = 0x02
		self.ENTRYSHIFTINC = 0x01
		self.ENTRYSHIFTDEC = 0x00

		# Flags for display on/off control
		self.DISP_ON = 0x04
		self.DISP_OFF = 0x00
		self.CURSOR_ON = 0x02
		self.CURSOR_OFF = 0x00
		self.BLINK_ON = 0x01
		self.BLINK_OFF = 0x00

		# Flags for display/cursor shift
		self.DISPMOVE = 0x08
		self.CURSORMOVE = 0x00
		self.MOVE_RIGHT = 0x04
		self.MOVE_LEFT = 0x00

		# Flags for function set
		self.MODE_8BIT = 0x10
		self.MODE_4BIT = 0x00
		self.LCD_2LINE = 0x08
		self.LCD_1LINE = 0x00
		self.LCD_5x10DOTS = 0x04
		self.LCD_5x8DOTS = 0x00

		# Backlight control
		self.BACKLIGHT_ON = 0x08
		self.BACKLIGHT_OFF = 0x00

		self.en = 0x04 # enable bit 
		self.rw = 0x02 # read/write bit
		self.rs = 0x01 # register select bit

		self.backlight = 0x08
		self.displaymode = 0x00
		self.displaycontrol = 0x00
		self.displayfunction = 0x00

		# Sets LCD to correct state
		def begin(self):
			self.displayfunction = self.MODE_4BIT | self.LCD_2LINE | self.LCD_5x8DOTS

			time.sleep_ms(50)

			# set up backlight
			self.expanderWrite(self.backlight)
			time.sleep_ms(1000)

			# first try
			self.write4bits(0x03 << 4)
			time.sleep_us(4500)
			# second try
			self.write4bits(0x03 << 4)
			time.sleep_us(4500)
			# last try
			self.write4bits(0x03 << 4)
			time.sleep_us(150)

			# set up 4 bit interface
			self.write4bits(0x02 << 4)

			# set no. of lines, font size etc. 
			self.command(self.CMD_FUNCSET | self.displayfunction)

			# turn on display with no cursor and no blinking
			self.displaycontrol = self.DISP_ON | self.CURSOR_OFF | self.BLINK_OFF
			self.display()

			# clear the screen
			self.clear()

			# initialize to default text direction
			self.displaymode = self.ENTRYLEFT | self.ENTRYSHIFTDEC

			#set entry mode
			self.command(self.CMD_ENTRYMODESET | self.displaymode)

			self.home()


		def printLeft(self):
			pass

		def printRight(self):
			pass

		def shiftInc(self):
			pass

		def shiftDec(self):
			pass

		## High Level Commands for the user

		# Remove all characters currently shown. 
		# Next print/write op will start from first position on LCD display
		def clear(self):
			self.command(self.CMD_CLEARDISP)
			time.sleep_us(2000)

		# Next print/write op will start from first position on LCD display
		def home(self):
			self.command(self.CMD_RETURNHOME)
			time.sleep_us(2000)

		def setCursor(self, _col, _row):
			row_offsets = [0x00, 0x40, 0x14, 0x54]
			if (_row > 2):
				_row = 1
			self.command(self.CMD_SETDDRAMADDR | (col + row_offsets[_row]))

		# Do not show any characters on LCD
		# Backlight remains unchanged
		# All characters written on the display will return when re-enabled
		def noDisplay(self):
			self.displaycontrol &= ~self.DISP_ON
			self.command(self.CMD_DISPCNTR | self.displaycontrol)

		# Show characters on LCD, to be called after noDisplay()
		def display(self):
			self.displaycontrol |= self.DISP_ON
			self.command(self.CMD_DISPCNTR | self.displaycontrol)

		# Do not show cursor
		def noCursor(self):
			self.displaycontrol &= ~self.CURSOR_ON
			self.command(self.CMD_DISPCNTR | self.displaycontrol)

		# Show cursor indecator, which can be blinked by blink() and noBlink()
		def cursor(self):
			self.displaycontrol |= self.CURSOR_ON
			self.command(self.CMD_DISPCNTR | self.displaycontrol)

		# Do not blink cursor
		def noBlink(self):
			self.displaycontrol &= ~self.BLINK_ON
			self.command(self.CMD_DISPCNTR | self.displaycontrol)

		# Start blinking the cursor
		def blink(self):
			self.displaycontrol |= self.BLINK_ON
			self.command(self.CMD_DISPCNTR | self.displaycontrol)

		# Scroll the display without changing RAM
		def scrollDisplayLeft(self):
			self.command(self.CMD_CURSORSHIFT | self.DISPMOVE | self.MOVE_LEFT)

		def scrollDisplayRight(self):
			self.command(self.CMD_CURSORSHIFT | self.DISPMOVE | self.MOVE_RIGHT)

		# Text flows from left to right
		def leftToRight(self):
			self.displaymode |= self.ENTRYLEFT
			self.command(self.CMD_ENTRYMODESET | self.displaymode)

		# Text flows from right to left
		def rightToLeft(self):
			self.displaymode &= ~self.ENTRYLEFT
			self.command(self.CMD_ENTRYMODESET | self.displaymode)	

		# 'Right justify' text from cursor
		def setAutoscroll(self):
			self.displaymode |= self.ENTRYSHIFTINC
			self.command(self.CMD_ENTRYMODESET | self.displaymode)

		# 'Left justify' text from cursor
		def noAutoscroll(self):
			self.displaymode &= ~self.ENTRYSHIFTINC
			self.command(self.CMD_ENTRYMODESET | self.displaymode)

		## Fills the first 8 CGRAM locations with custom characters
		def createChar(self, _location, _charmap):
			_location &= 0x7
			self.command(self.CMD_SETCGRAMADDR| (_location << 3))
			for char in _charmap:
				self.write(char)

		## Control Backlight
		def noBacklight(self):
			self.backlight = self.BACKLIGHT_OFF
			self.expanderWrite(0)

		def setBacklight(self):
			self.backlight = self.BACKLIGHT_ON
			self.expanderWrite(0)

		## Mid level commands, for sending commands/data
		def command(self, _value):
			self.send(_value, 0)

		def write(self, _value):
			send(_value, self.rs)
			return 1

		## Low level data pushing commands
		def send(self, _value, _mode):
			highnib = _value & 0xf0
			lownib = (_value & 0x0f) << 4
			self.write4bits(highnib | _mode)
			self.write4bits(lownib | _mode)

		def write4bits(self, _value):
			self.expanderWrite(_value)
			self.pulseEnable(_value)

		def expanderWrite(self, _data):
			self.i2c.writeto(self.ID, str(_data|self.backlight).encode())

		def pulseEnable(self, _data):
			self.expanderWrite(_data|self.en)
			time.sleep_us(1)

			self.expanderWrite(_data & ~self.en)
			time.sleep_us(50)


		def load_custom_char(self, char_num, rows):
			self.createChar(char_num, rows)

		def printstr(self):
			pass


def main():
	i2c = machine.I2C(scl = machine.Pin(5), sda = machine.Pin(4), freq = 100000)
	screen = LCD(i2c)

if __name__ == "__main__":
	main()
