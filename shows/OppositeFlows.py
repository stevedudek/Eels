from color import hsv_multi_morph, randColor, shiftColor

from HelperFunctions import*

class Flow(object):
	def __init__(self, eel, color, d):
		self.eel_num = eel
		self.color = shiftColor(color, 0.2)
		self.size = randint(12, 24) * getSegmentRatio(eel)
		self.dir = d	# either 1 or -1
		self.pace = self.dir * getSegmentRatio(eel)
		self.pos = -(self.size/4) if d == 1 else getEelSize(eel)+(self.size/4)

	def get_flow_info(self):
		return makePacketDictionary(getPacket(self.pos, self.size, self.eel_num, 0.0, 1.0, False), self.color)

	def update_flow(self):
		if -(self.size/4) <= self.pos <= getEelSize(self.eel_num)+(self.size/4):
			self.pos += self.pace
			return True
		return False

class OppositeFlows(object):
	def __init__(self, eelmodel):
		self.name = "OppositeFlows"
		self.eel = eelmodel
		self.flows = []
		self.color1 = randColor()
		self.color2 = randColor()
		self.speed = 0.1
		          
	def next_frame(self):
		
		while (True):

			if len(self.flows) == 0:
				self.eel.black_all_cells()
				self.color1 = self.color2
				self.color2 = randColor()

				for e in range(numEels()):
					forward = Flow(e, self.color1, 1)
					reverse = Flow(e, self.color2, -1)
					self.flows.append(forward)
					self.flows.append(reverse)

			self.draw_flows([f.get_flow_info() for f in self.flows])

			for f in self.flows:
				if f.update_flow() == False:
					self.flows.remove(f)

			yield self.speed

	def draw_flows(self, flow_dicts):
		combined_dict = {coord: hsv_multi_morph(colors, True) for coord, colors in combinePacketDictionary(flow_dicts).iteritems()}
		for coord, color in combined_dict.iteritems():
			self.eel.set_cell(coord, color)
