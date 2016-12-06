from random import random, randint, choice
from math import sin
from eel import EEL_MAP, ALL_EELS, SEGMENT, LEDS
from color import HSV
#
# Constants
#

NUM_PIXELS = 144
maxColor = 1536

#
# Common random functions
#

# Random chance. True if 1 in Number
def oneIn(chance):
	return True if randint(1,chance) == 1 else False

# Return either 1 or -1
def plusORminus():
	return (randint(0,1) * 2) - 1

# Increase or Decrease a counter with a range
def upORdown(value, amount, min, max):
	value += (amount * plusORminus())
	return bounds(value, min, max)

# Increase/Decrease a counter within a range
def inc(value, increase, min, max):
	value += increase
	return bounds(value, min, max)

def bounds(value, min, max):
	if value < min:
		value = max
	if value > max:
		value = min
	return value

# Number of eels
def numEels():
	return len(EEL_MAP)

# Get the number of segments (tubes)
def numSegments():
	return sum([size for (size, direct) in EEL_MAP])

# Get an array of (e,l) coordinates for the position (0-11) on all segments (tubes)
def getPixelsPosAllEels(pos):
	return sum([[(e,l) for l in getPixelsPos(pos, e)] for e in range(numEels()-1)], [])

# Get an array of light positions for the particular pixel position (0-11)
def getPixelsPos(pos, eel):
	return [(pos % SEGMENT) + (i * SEGMENT) for i in range(getEelSegment(eel)-1)]

# Get a random eel
def randEel():
	return randint(0, len(EEL_MAP)-1)

# Return a random pixel from the canonical segment size
def randSegment():
	return randint(0, SEGMENT-1)

# Return a random light from the longest eel
def randLight():
	return randint(0, getLongestEel()-1)

# Get a random pixel from a particular eel. Default is from any eel.
def randEelPixel(eel=ALL_EELS):
	if eel == ALL_EELS:
		eel = randEel()
	light = randint(0, getEelSize(eel)-1)
	return (eel, light)

# Get the length of the eel in number of pixels
def getEelSize(eel):
	return getEelSegment(eel) * SEGMENT

# Return the length of the longest eel in pixels
def getLongestEel():
	return SEGMENT * getMaxEelSegment()

# Return the fractional eel length with the longest eel at 1.0
def getSegmentRatio(eel):
	return 1.0 * getEelSegment(eel) / getMaxEelSegment()

# Return the segment length of the longest eel
def getMaxEelSegment():
	return max([size for (size, direct) in EEL_MAP])

# Get the number of segments in the eel
def getEelSegment(eel):
	(size, direct) = EEL_MAP[eel]
	return size

# Get the number of total Pixels (LEDS)
def allPixelSize():
	return sum([(size * SEGMENT) for (size, direct) in EEL_MAP])

# Calculate a packet. Return a tuple array of ((eel, light), intensity) for the entire eel
# Intensity = 0-1
# center = any value
# size = light width of sine function
def getPacket(center, size, e, Min=0.0, Max=1.0, wrap=True):
	if e == ALL_EELS:
		return sum([getPacket(center, size, eel, Min, Max, wrap) for eel in range(numEels())],[])
	return [((e, l), calcPacket(center, size, l, Min, Max, wrap)) for l in range(getEelSize(e))]

def calcPacket(center, size, pos, Min, Max, wrap):
	pos -= (center - (size / 2.0))
	while pos < 0 and wrap:
		pos += SEGMENT
	while pos >= SEGMENT and wrap:
		pos -= SEGMENT
	if 0 < pos < size:
		amount = sin(3.14 * Max * pos / size)
		return amount if amount >= Min else 0
	else:
		return 0

# Calculate a wave. Return a tuple array of ((eel, light), intensity) for the entire eel
# Intensity = 0-1
# start = 0-12 but can be more or less
# size = light width of sine function
def getWave(center, size, e, Min=0.0, Max=1.0):
	if e == ALL_EELS:
		return sum([getWave(center, size, eel, Min, Max) for eel in range(numEels())],[])
	return [((e, l), calcPacket(center % getEelSize(e), size, l, Min, Max, True)) for l in range(getEelSize(e))]

def calcWave(center, size, pos, Min, Max):
	pos -= (center - (size / 2.0))
	amount = abs(sin(3.14 * Max * pos / size))
	return amount if amount >= Min else 0

# Convert packet or wave into a dictionary of {coord:color}
def makePacketDictionary(packet, color):
	return {(e,l): HSV(color.h, color.s, value) for ((e, l), value) in packet}

def combinePacketDictionary(dicts):
	unique_coords = set(sum([d.keys() for d in dicts], []))
	return {k: [d[k] for d in dicts if k in d] for k in unique_coords}
