from color import HSV, randColor, shiftColor

from HelperFunctions import*
	
class Inversion(object):
	def __init__(self, eelmodel):
		self.name = "Inversion"
		self.eel = eelmodel
		self.speed = randint(1,10) / 20.0
		self.start = getLongestEel() - 1
		self.size = randint(6, 12)	# Don't go below 3
		self.fraction = 1
		self.color1 = randColor()
		self.color2 = randColor(False)
		          
	def next_frame(self):

		while (True):

			packet = makePacketDictionary(getPacket(self.start, self.size, ALL_EELS), self.color1)

			for coord, color in packet.iteritems():
				(e,l) = coord
				if l % self.fraction:
					color = HSV(self.color1.h, self.color1.s, color.v)
				else:
					color = HSV(self.color2.h, self.color2.s, color.v)
				self.eel.set_cell(coord, color)

			if oneIn(500):
				self.size = upORdown(self.size, 1, 6, 18)

			if oneIn(500):
				self.speed = upORdown(self.speed, 0.05, 0.05, 0.5)

			if oneIn(100):
				self.fraction += 1
				if self.fraction > 6:
					self.fraction = 1
					self.color2 = self.color1
					self.color2 = randColor()

			self.start -= 1

			if self.start < 0:
				self.start += getLongestEel()
				self.color2 = shiftColor(self.color2, 0.05)

			yield self.speed
