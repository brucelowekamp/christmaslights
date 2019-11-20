import array
from utils import *

USE_RELAYS = True #disable AC relay/GPIO (universe 10)

class Relays(object):
  def __init__(self, wrapper):
    self._dmx = array.array('B', [0, 0, 0])
    self._draw = False
    self._universe = 10
    self._wrapper = wrapper

  @property
  def draw_pending(self):
    return self._draw
  
  def on(self, channel):
    self._dmx[channel] = 255
    self._draw = True

  def off(self, channel):
    self._dmx[channel] = 0
    self._draw = True


  def SendDmx(self):
    if(USE_RELAYS and self._draw): self._wrapper.Client().SendDmx(self._universe, self._dmx, DmxSent)
    self._draw = False
