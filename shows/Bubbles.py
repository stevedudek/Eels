from color import HSV, randColor, shiftColor

from HelperFunctions import*

class Bubble(object):
	def __init__(self, eelmodel, color, pos, age = 0.25, intense = 0, growing = True):
		self.eel = eelmodel
		self.color = color
		self.pos = pos
		self.intense = intense
		self.age = age
		self.growing = growing

	def draw_sparkle(self):
		self.eel.set_cell(self.pos, self.color)

	def set_black(self):
		self.eel.black_cell(self.pos)

	def fade_sparkle(self):
		if self.growing == True:
			self.intense += self.age
			if self.intense >= 1.0:
				self.intense = 1
				self.growing = False
			return True
		else:
			self.intense -= self.age
			return (self.intense > 0)

class Bubbles(object):
	def __init__(self, eelmodel):
		self.name = "Bubbles"
		self.eel = eelmodel
		self.speed = randint(1,10) / 20.0
		self.start = 0
		self.size = randint(3, SEGMENT)
		self.color = randColor()
		          
	def next_frame(self):
		
		while (True):

			packet = getPacket(self.start, self.size, ALL_EELS)

			for ((e,l), value) in packet:
				self.eel.set_cell((e,l), HSV(self.color.h, self.color.s, value))

			if oneIn(100):
				self.color = shiftColor(self.color)

			if oneIn(500):
				self.size = upORdown(self.size, 1, 1, SEGMENT)

			if oneIn(500):
				self.speed = upORdown(self.speed, 0.05, 0.05, 0.5)

			if oneIn(round((1.1 - self.speed) * 50)):
				self.eel.set_all_cells(randColor())	# Blink!

			self.start += 1
			if self.start >= getLongestEel():
				self.start -= getLongestEel()

			yield self.speed
