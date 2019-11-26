from ola.ClientWrapper import ClientWrapper
from PixelDisplay import PixelDisplay
from PixelPatterns import PixelPatterns
from Relays import Relays
from Sparkler import *
import argparse
import array
import gc
import random
import time

TICK_INTERVAL_MS = 50  # in ms
TICK_INTERVAL_S = TICK_INTERVAL_MS/1000.0
TICK_PER_SEC = 1000//TICK_INTERVAL_MS

GPIO_FANS = 0
GPIO_OLAF = 1
GPIO_GRINCH = 2


class Show(object):

  def __init__(self, options):
    self._SLIDE_START_MS = options.startslide*1000
    self._DARK_TIME_MS = options.darktime*1000
    self._options = options
    PixelPatterns.SetOptions(options)
    self._wrapper = ClientWrapper()

    self._loop_count = 0
    self._relays = None
    self._display = None
    self._sliding = None
    self._target_time = time.time()

  @staticmethod
  def SetArgs(parser):
    parser.add_argument('--startslide', type=int, default=100, help="start grinch slide at seconds")
    parser.add_argument('--darktime', type=int, default=6, help="time to remain dark after slide before reset")
    parser.add_argument('--pattern', type=int, help="run only pattern index i")
    
  def StartSlide(self):
    print "start slide"
    gc.collect()
    self._sliding = self._display.SlideLeft()
    self._sparkler = None

  def NewDisplay(self):
    gc.collect()
    self._loop_count = 0
    self._sliding = None
    self._display = PixelDisplay(self._wrapper, self._options)
    self._relays = Relays(self._wrapper, self._options)
    if (self._options.pattern is not None):
      pattern = PixelPatterns.Patterns[self._options.pattern]
    else:
      pattern = random.choice(PixelPatterns.Patterns)
    self._sparkler = pattern(self._display)
    self._wrapper.AddEvent(0, lambda: self._relays.on(GPIO_FANS))
    self._wrapper.AddEvent(0, lambda: self._relays.on(GPIO_OLAF))
    self._wrapper.AddEvent(0, lambda: self._relays.off(GPIO_GRINCH))
    self._wrapper.AddEvent(self._SLIDE_START_MS-3000, lambda: self._relays.off(GPIO_OLAF))
    self._wrapper.AddEvent(self._SLIDE_START_MS-3000, lambda: self._relays.on(GPIO_GRINCH))
    self._wrapper.AddEvent(self._SLIDE_START_MS, lambda: self.StartSlide())
    self._wrapper.AddEvent(0, lambda: self._relays.off(GPIO_GRINCH))
    #self._wrapper.AddEvent(self._RESET_DISPLAY_MS, lambda: self.NewDisplay())

  # send frame precomputed last call, then compute frame and schedule next call
  def SendFrame(self):
    # send (if pending), do first thing to time as precisely as we can
    self._display.SendDmx()
    self._relays.SendDmx()
    if (self._loop_count % (TICK_PER_SEC*10) == 0):
      print "loop: ", self._loop_count // TICK_PER_SEC
    
    if (self._sliding is not None):
      if (not self._sliding.next()):
        self._wrapper.AddEvent(self._DARK_TIME_MS, lambda: self.NewDisplay())
        self._sliding = None
    elif (self._sparkler is not None):
      self._sparkler.Sparkle()
      
    # schedule a function call for remaining time
    # we do this last with the right sleep time in case the frame computation takes a long time.
    next_target = self._target_time + TICK_INTERVAL_S
    delta_time = next_target - time.time()
    if (delta_time < 0): #hiccup, fell behind, one extra call
      self._target_time = time.time()+0.001 # make an extra call faking one ms progress, drop the rest
      print "hiccup!"
      self.SendFrame()
    else:
      self._target_time = next_target
      self._wrapper.AddEvent(int(delta_time*1000), lambda: self.SendFrame())

    self._loop_count += 1

  def Run(self):
    self.NewDisplay()
    self.SendFrame()
    self._wrapper.Run()

    
def main():
  parser = argparse.ArgumentParser()
  Show.SetArgs(parser)
  PixelDisplay.SetArgs(parser)
  Relays.SetArgs(parser)
  PixelPatterns.SetArgs(parser)
  Sparkler.SetArgs(parser)
  options = parser.parse_args()
  print "args are" , options
  show = Show(options)
  show.Run()


if __name__ == '__main__':
  main()
