import array
from ola.ClientWrapper import ClientWrapper
from PixelDisplay import PixelDisplay
from PixelPatterns import PixelPatterns
from Relays import Relays
import time
import random

TICK_INTERVAL_MS = 50  # in ms
TICK_INTERVAL_S = TICK_INTERVAL_MS/1000.0
TICK_PER_SEC = 1000//TICK_INTERVAL_MS

GPIO_FANS = 0
GPIO_OLAF = 1
GPIO_GRINCH = 2


class Show(object):

  def __init__(self):
    self._SLIDE_START_MS = 100*1000
    self._RESET_DISPLAY_MS = 120*1000

    self._wrapper = ClientWrapper()

    self._loop_count = 0
    self._relays = None
    self._display = None
    self._sliding = False
    self._target_time = time.time()

    
  def StartSlide(self):
    print "start slide"
    self._sliding = True

  def NewDisplay(self):
    self._loop_count = 0
    self._sliding = False
    self._display = PixelDisplay(self._wrapper)
    self._relays = Relays(self._wrapper)
    random.choice(PixelPatterns)(self._display)
    self._wrapper.AddEvent(0, lambda: self._relays.on(GPIO_FANS))
    self._wrapper.AddEvent(0, lambda: self._relays.on(GPIO_OLAF))
    self._wrapper.AddEvent(0, lambda: self._relays.off(GPIO_GRINCH))
    self._wrapper.AddEvent(self._SLIDE_START_MS-3000, lambda: self._relays.off(GPIO_OLAF))
    self._wrapper.AddEvent(self._SLIDE_START_MS-3000, lambda: self._relays.on(GPIO_GRINCH))
    self._wrapper.AddEvent(self._SLIDE_START_MS, lambda: self.StartSlide())
    self._wrapper.AddEvent(0, lambda: self._relays.off(GPIO_GRINCH))
    self._wrapper.AddEvent(self._RESET_DISPLAY_MS, lambda: self.NewDisplay())

  # send frame precomputed last call, then compute frame and schedule next call
  def SendFrame(self):
    # send (if pending), do first thing to time as precisely as we can
    self._display.SendDmx()
    self._relays.SendDmx()
    if (self._loop_count % (TICK_PER_SEC*10) == 0):
      print "loop: ", self._loop_count // TICK_PER_SEC
    
    draw = False
  
    if (self._sliding):
      self._sliding = self._display.SlideLeft()
      draw = True

    # schedule a function call for remaining time
    # we do this last with the right sleep time in case the frame computation takes a long time.
    next_target = self._target_time + TICK_INTERVAL_S
    delta_time = next_target - time.time()
    if (delta_time < 0): #hiccup, fell behind, one extra call
      self._target_time = time.time()+0.001 # make an extra call faking one ms progress, drop the rest
      print "hiccup!"
      SendFrame()
    else:
      self._target_time = next_target
      self._wrapper.AddEvent(int(delta_time*1000), lambda: self.SendFrame())

    self._loop_count += 1

show = Show()
show.NewDisplay()
show.SendFrame()
show._wrapper.Run()
