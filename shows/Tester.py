from color import randColor, shiftColor
from random import choice

from HelperFunctions import*
	
class Tester(object):
	def __init__(self, eelmodel):
		self.name = "Tester"        
		self.eel = eelmodel
		self.speed = 0.2
		self.color = randColor()
		self.all_cells = self.eel.all_cells()
		          
	def next_frame(self):
		
		while (True):
			
			self.eel.black_all_cells()
					
			self.eel.set_cells([choice(self.all_cells) for i in 4*range(numSegments())], shiftColor(self.color, 0.2))

			if oneIn(100):
				self.color = shiftColor(self.color)

			yield self.speed