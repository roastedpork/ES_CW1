# Buffer class to implement a moving average filter for the input data
# implements a FIFO queue for the inputs

class Buffer:
	def __init__(self, _period = 10):
		self.buffer = [0.0 for i in range(_period)]

	def getMA(self):
		return sum(self.buffer)/len(self.buffer)

	def update(self, _input):
		self.buffer = [_input] +self.buffer[:-1]

	def changeMAPeriod(self, _period):
		if _period < len(self.buffer):
			self.buffer = self.buffer[:_period]
		elif _period > len(self.buffer):
			self.buffer += [0 for i in range(_period - len(self.buffer))]