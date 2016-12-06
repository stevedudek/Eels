"""
Model to communicate with a Eel simulator over a TCP socket

"""
import socket
from color import restrict_color

# "off" color for simulator
SIM_DEFAULT = (188,210,229) # BCD2E5

class SimulatorModel(object):
    def __init__(self, hostname, port=4444, debug=False):
        self.server = (hostname, port)
        self.debug = debug
        self.sock = None

        # list of (strip,pixel) to be sent on the next call to go
        self.dirty = {}

        self.connect()

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.server)
        # XXX throw an exception if the socket isn't available?

    def __repr__(self):
        return "Eel Model(%s, port=%d, debug=%s)" % (self.server[0], self.server[1], self.debug)

    # Model basics

    def set_cell(self, cell, color):
        "Set a (strip,pixel) coord to a color"
        self.dirty[cell] = color

    def set_cells(self, cells, color):
        "Set all fixtures in a list of coordinates to a color"
        for cell in cells:
            self.set_cell(cell, color)

    def go(self):
        "Send all of the buffered commands"
        self.send_start()

        for (cell, color) in self.dirty.items():
            (strip, pixel) = cell
            (r,g,b) = self.translate_color(color)
            
            msg = "%s,%s,%s,%s,%s" % (strip, pixel, r,g,b)
            
            if self.debug:
                print msg
            self.sock.send(msg)
            self.sock.send('\n')

        self.dirty = {}

    def send_start(self):
        "send a start signal"
        msg = "X"   # tell processing that commands are coming

        if self.debug:
            print msg
        self.sock.send(msg)
        self.sock.send('\n')

    def send_delay(self, delay):
        "send a morph amount in milliseconds"
        msg = "D%s" % (str(int(delay * 1000)))

        if self.debug:
            print msg
        self.sock.send(msg)
        self.sock.send('\n')

    def relay_OSC_cmd(self, cmd, value):
        "Relay to Processing the OSC command"
        msg = "OSC,%s,%s" % (cmd,value)

        if self.debug:
            print msg
        self.sock.send(msg)
        self.sock.send('\n')

    def translate_color(self, color):
        """Convert the hsv color object into rgb"""
        corrected = restrict_color(color, -0.05, 0.15) # RED clipping happens here
        #corrected = color
        return (corrected.r, corrected.g, corrected.b)