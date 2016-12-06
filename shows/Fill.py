from color import randColor, shiftColor
from random import shuffle

from HelperFunctions import*
	
class Fill(object):
	def __init__(self, eelmodel):
		self.name = "Fill"
		self.eel = eelmodel
		self.speed = randint(1,5) / 20.0
		self.color = HSV(0,0,0)
		self.cells = []
		          
	def next_frame(self):

		while (True):

			if not self.cells:
				self.cells = self.eel.all_cells()
				shuffle(self.cells)
				self.color = randColor() if self.color.v == 0 else HSV(0,0,0)

			self.eel.set_cell(self.cells[0], shiftColor(self.color, 0.04))
			self.cells = self.cells[1:]

			if oneIn(500):
				self.speed = upORdown(self.speed, 0.05, 0.05, 0.25)

			yield self.speed

