from color import HSV, adj_value, randColor, shiftColor

from HelperFunctions import*

class Wave(object):
	def __init__(self, eelmodel):
		self.name = "Wave"
		self.eel = eelmodel
		self.speed = randint(1,10) / 20.0
		self.start = 0
		self.size = randint(SEGMENT/2, SEGMENT)
		self.color = randColor()
		          
	def next_frame(self):
		
		while (True):

			wave = makePacketDictionary(getWave(self.start, self.size, ALL_EELS), self.color)

			for coord, color in wave.iteritems():
				(e,l) = coord
				self.eel.set_cell(coord, HSV(adj_value(color.h + (l * 0.01)), color.s, color.v))

			if oneIn(100):
				self.color = shiftColor(self.color)

			if oneIn(500):
				self.size = upORdown(self.size, 1, SEGMENT, SEGMENT)

			if oneIn(500):
				self.speed = upORdown(self.speed, 0.05, 0.05, 0.5)

			self.start += 1
			if self.start >= getLongestEel():
				self.start -= getLongestEel()

			yield self.speed
