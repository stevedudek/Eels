from color import hsv_multi_morph, randColor, shiftColor

from HelperFunctions import*

class Bulge(object):
	def __init__(self, color, age = 0.25):
		self.eel_num = randEel()
		self.color = shiftColor(color, 0.2)
		self.size = randint(1,3)
		self.start = randint(1-self.size, 11)
		self.intense = 0
		self.age = age
		self.growing = True

	def get_bulge_info(self):
		return makePacketDictionary(getPacket(self.start, self.size, self.eel_num, 0, self.intense), self.color)

	def update_bulge(self):
		if self.growing == True:
			self.intense += self.age
			if self.intense >= 1.0:
				self.intense = 1
				self.growing = False
			return True
		else:
			self.intense -= self.age
			return (self.intense > 0)

class Bulges(object):
	def __init__(self, eelmodel):
		self.name = "Bulges"
		self.eel = eelmodel
		self.bulges = []
		self.bulge_num = numSegments() * 3
		self.color = randColor()
		self.speed = 0.2
		          
	def next_frame(self):
		
		while (True):

			while len(self.bulges) < self.bulge_num:
				new_bulge = Bulge(self.color, randint(1,6) / 20.0)
				self.bulges.append(new_bulge)

			self.draw_bulges([b.get_bulge_info() for b in self.bulges])

			for b in self.bulges:
				if not b.update_bulge():
					self.bulges.remove(b)

			if oneIn(100):
				self.color = shiftColor(self.color)

			yield self.speed

	def draw_bulges(self, bulge_dicts):
		combined_dict = {coord: hsv_multi_morph(colors) for coord, colors in combinePacketDictionary(bulge_dicts).iteritems()}
		for coord, color in combined_dict.iteritems():
			self.eel.set_cell(coord, color)
