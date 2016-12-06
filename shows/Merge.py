from color import hsv_multi_morph, randColor, shiftColor

from HelperFunctions import*

class Merge(object):
	def __init__(self, eelmodel):
		self.name = "Merge"
		self.eel = eelmodel
		self.color1 = randColor()
		self.color2 = randColor()
		self.size = 0
		self.growing = True
		self.speed = randint(1,10) / 20.0
		          
	def next_frame(self):
		
		while (True):

			packets1 = [makePacketDictionary(getPacket(0, self.size * getSegmentRatio(e), e), self.color1) for e in range(numEels())]
			packets2 = [makePacketDictionary(getPacket(getEelSize(e)+self.size, self.size * getSegmentRatio(e), e), self.color2) for e in range(numEels())]

			self.draw_flows(packets1 + packets2)

			if self.growing:
				self.size += 1
				if self.size > SEGMENT: #getLongestEel() / 2:
					self.growing = False
			else:
				self.size -= 1
				if self.size <= 1:
					self.growing = True
					self.color2 = self.color1
					self.color1 = randColor()

			if oneIn(500):
				self.speed = upORdown(self.speed, 0.05, 0.05, 0.5)

			yield self.speed

	def draw_flows(self, flow_dicts):
		combined_dict = {coord: hsv_multi_morph(colors, True) for coord, colors in combinePacketDictionary(flow_dicts).iteritems()}
		for coord, color in combined_dict.iteritems():
			self.eel.set_cell(coord, color)
