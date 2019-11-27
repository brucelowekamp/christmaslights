import array
from utils import *

class Relays(object):
  def __init__(self, wrapper, options):
    self._dmx = array.array('B', [0] * 13)
    self._draw = False
    self._universe = 10
    self._wrapper = wrapper
    self._use_relays = options.relays

  @staticmethod
  def SetArgs(parser):
    parser.add_argument('--norelays', dest="relays", action='store_false', help="disable relays/gpio")

  @property
  def draw_pending(self):
    return self._draw
  
  def on(self, channel):
    print "relay on", channel
    self._dmx[channel] = 255
    self._draw = True

  def off(self, channel):
    print "relay off", channel
    self._dmx[channel] = 0
    self._draw = True


  def SendDmx(self):
    if(self._use_relays and self._draw): self._wrapper.Client().SendDmx(self._universe, self._dmx, DmxSent)
    self._draw = False
