from color import hsv_multi_morph, randColor, shiftColor

from HelperFunctions import*

class SimpleCenters(object):
	def __init__(self, eelmodel):
		self.name = "SimpleCenters"
		self.eel = eelmodel
		self.color = randColor()
		self.size = 0
		self.pos = 0
		self.growing = True
		self.speed = randint(1,10) / 20.0
		          
	def next_frame(self):
		
		while (True):

			for e in range(numEels()):
				packets = [makePacketDictionary(getPacket(self.pos + (s * SEGMENT), self.size, e), self.color) for s in range(getEelSegment(e))]
				self.draw_flows(packets)

			if self.growing:
				self.size += 1
				if self.size > SEGMENT:
					self.growing = False
			else:
				self.size -= 1
				if self.size <= 0:
					self.growing = True
					self.color = shiftColor(self.color)

			self.pos = (self.pos + 0.25) % SEGMENT

			if oneIn(500):
				self.speed = upORdown(self.speed, 0.05, 0.05, 0.5)

			yield self.speed

	def draw_flows(self, flow_dicts):
		combined_dict = {coord: hsv_multi_morph(colors, True) for coord, colors in combinePacketDictionary(flow_dicts).iteritems()}
		for coord, color in combined_dict.iteritems():
			self.eel.set_cell(coord, color)
