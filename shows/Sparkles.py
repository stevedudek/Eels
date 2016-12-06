from HelperFunctions import*
from color import randColor, shiftColor

class Sparkle(object):
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

        						
class Sparkles(object):
	def __init__(self, eelmodel):
		self.name = "Sparkles"        
		self.eel = eelmodel
		self.sparkles = []	# List that holds Sparkle objects
		self.speed = 0.2
		self.color = randColor()
		self.sparkle_perc = 10
		self.spark_num = LEDS * self.sparkle_perc / 100
		self.age = 0.1
	
	def next_frame(self):
		
		while (True):

			while len(self.sparkles) < self.spark_num:
				new_sparkle = Sparkle(self.eel, shiftColor(self.color), self.eel.rand_cell(), randint(1,40) / 100.0)
				self.sparkles.append(new_sparkle)
			
			# Draw the sparkles
				
			for s in self.sparkles:
				s.draw_sparkle()
				if not s.fade_sparkle():
					s.set_black()
					self.sparkles.remove(s)

			if oneIn(500):
				self.color = shiftColor(self.color)
			
			yield self.speed
