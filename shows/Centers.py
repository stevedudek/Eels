from color import hsv_multi_morph, randColor, shiftColor

from HelperFunctions import*

class Centers(object):
	def __init__(self, eelmodel):
		self.name = "Centers"
		self.eel = eelmodel
		self.color = randColor()
		self.size = 1
		self.growing = True
		self.speed = randint(1,10) / 20.0
		          
	def next_frame(self):
		
		while (True):

			packets = [makePacketDictionary(getPacket(5.5 + getEelSegment(e), self.size * getSegmentRatio(e), e), self.color) for e in range(numEels())]

			self.draw_flows(packets)

			if self.growing:
				self.size += 1
				if self.size > getLongestEel():
					self.growing = False
			else:
				self.size -= 1
				if self.size < 2:
					self.growing = True
					self.color = shiftColor(self.color)

			if oneIn(500):
				self.speed = upORdown(self.speed, 0.05, 0.05, 0.5)

			yield self.speed

	def draw_flows(self, flow_dicts):
		combined_dict = {coord: hsv_multi_morph(colors, True) for coord, colors in combinePacketDictionary(flow_dicts).iteritems()}
		for coord, color in combined_dict.iteritems():
			self.eel.set_cell(coord, color)
