"""
Model to communicate with a Eel simulator over a TCP socket

"""

from random import choice
from color import HSV

"""
Coordinates: (e,l) = (x,y) = (eel,light)

"""

EEL_MAP = [(4, 'R'), (4, 'F'), (4, 'F'), (4, 'R'), (4, 'F'), (4, 'F')]

LEDS = 144
SEGMENT = 12

ALL_EELS = 99

def load_eels(model):
    return Eel(model)

class Eel(object):

    """
    Eel coordinates are stored in a hash table.
    Keys are (e,l) coordinate tuples
    Values are (strip, pixel) tuples
    
    Frames implemented to shorten messages:
    Send only the pixels that change color
    Frames are hash tables where keys are (e,l) coordinates
    and values are (h,s,v) colors
    """
    def __init__(self, model):
        self.model = model
        self.cellmap = self.add_strips()
        self.curr_frame = {}
        self.next_frame = {}
        self.init_frames()

    def __repr__(self):
        return "Eels(%s)" % (self.model, self.side)

    def all_cells(self):
        """Return the list of valid coords"""
        return list(self.cellmap.keys())

    def cell_exists(self, coord):
        return self.cellmap[coord]

    def rand_cell(self):
        return choice(self.cellmap.keys())

    def set_cell(self, coord, color):
        (e,l) = coord
        if e == ALL_EELS and l < SEGMENT:
            for e,(size, direct) in enumerate(EEL_MAP):
                coords = [(e, (l*size)+i) for i in range(size)]
                self.set_cells(coords, color)
        else:
            if self.cell_exists(coord):
                self.next_frame[coord] = color

    def set_cells(self, coords, color):
        for coord in coords:
            self.set_cell(coord, color)

    def set_all_cells(self, color):
        for coord in self.all_cells():
            self.next_frame[coord] = color

    def black_cell(self, coord):
        self.set_cell(coord, HSV(0,0,0))

    def black_cells(self, coords):
        self.set_cells(coords, HSV(0,0,0))

    def black_all_cells(self):
        self.set_all_cells(HSV(0,0,0))

    def clear(self):
        self.force_frame()
        self.black_all_cells()
        self.go()

    def go(self):
        self.send_frame()
        self.model.go()
        self.update_frame()

    def send_delay(self, delay):
        self.model.send_delay(delay)

    def update_frame(self):
        for coord in self.next_frame:
            self.curr_frame[coord] = self.next_frame[coord]

    def send_frame(self):
        for coord,color in self.next_frame.items():
            if self.curr_frame[coord] != color: # Has the color changed? Hashing to color values
                self.model.set_cell(self.cellmap[coord], color)

    def force_frame(self):
        for coord in self.curr_frame:
            self.curr_frame[coord] = (-1,-1,-1)  # Force update

    def init_frames(self):
        for coord in self.cellmap:
            self.curr_frame[coord] = (0,0,0)
            self.next_frame[coord] = (0,0,0)

    def add_strips(self):
        cellmap = {}
        for e, (size,direct) in enumerate(EEL_MAP):
            (strip, start) = self.get_start_light_coord(e)
            for l in range(size * SEGMENT):
                pixel = start+l if direct == 'F' else start + (size * SEGMENT - l - 1)
                cellmap[(e,l)] = (strip, pixel)
        return cellmap

    def get_start_light_coord(self, eel_num):
        """Poll the EEL_MAP to find the the (strip,pixel) coordinate of the first light on the eel"""
        total_pixels = sum([size * SEGMENT for (size,dir) in EEL_MAP[:eel_num]])
        return (total_pixels // LEDS, total_pixels % LEDS)

##
## eel cell primitives
##

def is_on_board(coord):
    (p,d) = coord
    return (p < 6 and p > -6)