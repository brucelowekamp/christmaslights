import array
from Options import Options

class Relays(object):
  def __init__(self, wrapper):
    self._dmx = array.array('B', [0] * 13)
    self._draw = False
    self._universe = 10
    self._wrapper = wrapper
    self._use_relays = Options.relays

  @staticmethod
  def SetArgs(parser):
    parser.add_argument('--norelays', dest="relays", action='store_false', help="disable relays/gpio")

  @property
  def draw_pending(self):
    return self._draw
  
  def on(self, channel):
    #print "relay on", channel
    self._dmx[channel] = 255
    self._draw = True

  def off(self, channel):
    #print "relay off", channel
    self._dmx[channel] = 0
    self._draw = True

  @staticmethod
  def DmxSent(state):
    if not state.Succeeded():
      print ("Error: ", state.message)
      raise

  def SendDmx(self):
    if(self._use_relays and self._draw): 
      self._wrapper.Client().SendDmx(self._universe, self._dmx, Relays.DmxSent)
    self._draw = False
