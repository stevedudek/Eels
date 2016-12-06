from color import hsv_multi_morph, randColor, shiftColor

from HelperFunctions import*

class Wave(object):
	def __init__(self, color, age = 0.25, intense = 0, growing=True):
		self.eel_num = randEel()
		self.color = shiftColor(color)
		self.start = randLight()
		self.size = randint(3, 10)
		self.intense = intense
		self.age = age
		self.growing = growing

	def get_wave_info(self):
		return makePacketDictionary(getWave(self.start, self.size, self.eel_num, 0, self.intense), self.color)

	def update_wave(self):
		if self.growing:
			self.intense += self.age
			if self.intense >= 1.0:
				self.intense = 1
				self.growing = False
			return True
		else:
			self.intense -= self.age
			return (self.intense > 0)

class Waves(object):
	def __init__(self, eelmodel):
		self.name = "Waves"
		self.eel = eelmodel
		self.waves = []
		self.wave_num = numSegments()
		self.color = randColor()
		self.speed = 0.5
		          
	def next_frame(self):
		
		while (True):

			while len(self.waves) < self.wave_num:
				new_wave = Wave(self.color, randint(1,6) / 20.0)
				self.waves.append(new_wave)

			self.draw_waves([w.get_wave_info() for w in self.waves])

			for w in self.waves:
				if not w.update_wave():
					self.waves.remove(w)

			if oneIn(100):
				self.color = shiftColor(self.color)

			yield self.speed

	def draw_waves(self, wave_dicts):
		combined_dict = {coord: hsv_multi_morph(colors, True) for coord, colors in combinePacketDictionary(wave_dicts).iteritems()}
		for coord, color in combined_dict.iteritems():
			self.eel.set_cell(coord, color)
