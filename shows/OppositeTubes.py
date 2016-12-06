from color import hsv_multi_morph, randColor, shiftColor

from HelperFunctions import*

class Flow(object):
	def __init__(self, eel, color, dir):
		self.eel_num = eel
		self.color = shiftColor(color, 0.2)
		self.size = randint(6, 12) * getEelSegment(eel)
		self.dir = dir	# either 1 or -1
		self.pace = self.dir * getEelSegment(eel) / getMaxEelSegment()
		self.pos = 0 if dir == 1 else getLongestEel()

	def get_flow_info(self):
		return makePacketDictionary(getPacket(self.pos, self.size, self.eel_num, 0.0, 1.0, False), self.color)

	def update_flow(self):
		self.pos += self.pace
		return 0 < self.pos < getLongestEel()

class OppositeTubes(object):
	def __init__(self, eelmodel):
		self.name = "OppositeTubes"
		self.eel = eelmodel
		self.flows = []
		self.color1 = randColor()
		self.color2 = randColor()
		self.speed = randint(1,10) / 20.0
		          
	def next_frame(self):
		
		while (True):

			if len(self.flows) == 0:
				self.color1 = self.color2
				self.color2 = randColor()

				for e in range(numEels()):
					dir = 1 if e % 2 else -1
					color = self.color1 if e % 2 else self.color2
					new_flow = Flow(e, shiftColor(color), dir)
					self.flows.append(new_flow)

			self.draw_flows([f.get_flow_info() for f in self.flows])

			for f in self.flows:
				if f.update_flow() == False:
					self.flows.remove(f)

			if oneIn(500):
				self.speed = upORdown(self.speed, 0.05, 0.05, 0.5)

			yield self.speed

	def draw_flows(self, flow_dicts):
		combined_dict = {coord: hsv_multi_morph(colors, True) for coord, colors in combinePacketDictionary(flow_dicts).iteritems()}
		for coord, color in combined_dict.iteritems():
			self.eel.set_cell(coord, color)
