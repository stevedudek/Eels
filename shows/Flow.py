from color import HSV, randColor, shiftColor

from HelperFunctions import*
	
class Flow(object):
	def __init__(self, eelmodel):
		self.name = "Flow"
		self.eel = eelmodel
		self.speed = randint(1,10) / 20.0
		self.start = 0
		self.size = randint(3, 12)	# Don't go below 3
		self.color = randColor()
		          
	def next_frame(self):

		while (True):

			packet = makePacketDictionary(getPacket(self.start, self.size, ALL_EELS), self.color)

			for coord, color in packet.iteritems():
				self.eel.set_cell(coord, color)

			if oneIn(500):
				self.size = upORdown(self.size, 1, 3, SEGMENT)

			if oneIn(500):
				self.speed = upORdown(self.speed, 0.05, 0.05, 0.5)

			self.start += 1

			if self.start >= getLongestEel():
				self.start -= getLongestEel()
				self.color = shiftColor(self.color, 0.05)

			yield self.speed
