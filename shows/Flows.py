from color import hsv_multi_morph, randColor, shiftColor

from HelperFunctions import*

class OneFlow(object):
	def __init__(self, color):
		self.eel_num = randEel()
		self.color = shiftColor(color, 0.2)
		self.size = randint(2, 5)
		self.pos = -self.size
		self.pace = randint(1,10) / 20.0

	def get_flow_info(self):
		return makePacketDictionary(getPacket(self.pos, self.size, self.eel_num, 0.0, 1.0, False), self.color)

	def update_flow(self):
		self.pos += self.pace
		return (self.pos < getLongestEel() + self.size)

class Flows(object):
	def __init__(self, eelmodel):
		self.name = "Flows"
		self.eel = eelmodel
		self.flows = []
		self.flow_num = numSegments() * 2
		self.color = randColor()
		self.speed = 0.1
		          
	def next_frame(self):
		
		while (True):

			while len(self.flows) < self.flow_num:
				new_flow = OneFlow(self.color)
				self.flows.append(new_flow)

			self.draw_flows([f.get_flow_info() for f in self.flows])

			for f in self.flows:
				if f.update_flow() == False:
					self.flows.remove(f)

			if oneIn(100):
				self.color = shiftColor(self.color, 0.05)

			yield self.speed

	def draw_flows(self, flow_dicts):
		combined_dict = {coord: hsv_multi_morph(colors, True) for coord, colors in combinePacketDictionary(flow_dicts).iteritems()}
		for coord, color in combined_dict.iteritems():
			self.eel.set_cell(coord, color)
