import machine 
import vcnl4010 as Sensor 

def main(): 
	i2c = machine.I2C(scl = machine.Pin(5), sda = machine.Pin(4), freq = 100000) 
	
	SoilMoisture = Sensor.ALPSensor(i2c) 
	servopwm = machine.PWM(machine.Pin(12))
	servopwm.freq(50)
	
	timer = machine.RTC() 
	timer.alarm(0, 30000)
	
	while timer.alarm_left() > 0: 
		readout = SoilMoisture.getALReading() 
		
		if int (readout) < 500: 
			servopwm.duty(52)
		
		else: 
			servopwm.duty(103)

if __name__ == "__main__": 
	main() 
	
	

