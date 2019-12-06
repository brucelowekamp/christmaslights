try:
  from ola.ClientWrapper import ClientWrapper
except ImportError:
  print "NO OLA INSTALLED!!!  USING STUB OLA!!!"
  from OLAStubClientWrapper import ClientWrapper
from PixelDisplay import PixelDisplay
from PixelPatterns import PixelPatterns
from Relays import Relays
from Sparkler import Sparkler
import argparse
import array
import gc
import random
import time
import enum

TICK_INTERVAL_MS = 50  # in ms
TICK_INTERVAL_S = TICK_INTERVAL_MS/1000.0
TICK_PER_SEC = 1000//TICK_INTERVAL_MS

GPIO_FANS = 0
GPIO_OLAF = 1
GPIO_GRINCH = 2


class Show(object):

  # objects in show.  Ideally we get this via config but show variants use
  # the same objects (and pixels which are currently set up in PixelDisplay)
  class Relays(enum.IntEnum):
    # first 8 slots are SSR max 2A for lights
    OLAF = 0
    LASER_PROJ = 1
    REINDEER = 2
    SNOWMAN = 3
    GRINCH_SLEIGH = 4
    GRINCH = 5

    # next 4 are leaf relay max 10A for fans
    OLAF_FAN = 8
    GRINCH_FAN = 9
    GRINCH_SLEIGH_FAN = 10

    # last is local relay for 12V PS (for pixels)
    # relay is NC so we don't touch it during the show, used by show drivers 
    POWER = 12

  # Commands common (not involving animation)
  class Commands(enum.Enum):
    ON = 0
    OFF = 1
    PIXELS_ON = 3
    RESTART = 5

  def __init__(self, options):
    self._options = options
    PixelPatterns.SetOptions(options)
    self._wrapper = ClientWrapper()
    self._showcount = 0
    
    self._loop_count = 0
    self._relays = None
    self._display = None
    self._target_time = time.time()

  @staticmethod
  def SetArgs(parser):
    parser.add_argument('--pattern', type=int, help="run only pattern index i")
    parser.add_argument('--nosleigh', action='store_true', help="no grinch sleigh for high winds")

  @property
  def options(self):
    return self._options

  # begin show
  # subclass must override, call this, and minimally set up restart timer
  def ReStart(self):
    print "START"
    self._loop_count = 0
    self._display = PixelDisplay(self._wrapper, self._options)
    self._relays = Relays(self._wrapper, self._options)
    self._sparkler = None

  def NewDisplay(self):
    gc.collect()
    if (self._options.pattern is not None):
      pattern = PixelPatterns.Patterns[self._options.pattern]
    else:
      pattern = PixelPatterns.Patterns[self._showcount % len(PixelPatterns.Patterns)]
      self._showcount += 1
    self._sparkler = pattern(self._display)

  def LoadTiming(self, e):
    ms = int(e[0] * 1000)
    if (self._options.nosleigh and len(e) == 3):
      if (e[2] == Show.Relays.GRINCH_SLEIGH_FAN): e = (e[0], e[1], Show.Relays.GRINCH_FAN)
      elif (e[2] == Show.Relays.GRINCH_SLEIGH): e = (e[0], e[1], Show.Relays.GRINCH)
    # switch... oh yeah
    if (e[1] == Show.Commands.ON):
      self._wrapper.AddEvent(ms, lambda x=e[2]: self._relays.on(x))
    elif (e[1] == Show.Commands.OFF):
      self._wrapper.AddEvent(ms, lambda x=e[2]: self._relays.off(x))
    elif (e[1] == Show.Commands.PIXELS_ON):
      self._wrapper.AddEvent(ms, lambda: self.NewDisplay())
    elif (e[1] == Show.Commands.RESTART):
      self._wrapper.AddEvent(ms, lambda: self.ReStart())
    else:
      raise NotImplementedError(e)

  def LoadTimings(self, events):
    #print "adding events", events
    for e in events:
      self.LoadTiming(e)
        
  # stub subclasses can implement if they have their own animation
  def _animateNextFrame(self):
    pass

  # send frame precomputed last call, then compute frame and schedule next call
  def SendFrame(self):
    # send (if pending), do first thing to time as precisely as we can
    self._display.SendDmx()
    self._relays.SendDmx()
    if (self._loop_count % (TICK_PER_SEC*10) == 0):
      print "loop: ", self._loop_count // TICK_PER_SEC
    
    self._animateNextFrame()

    if (self._sparkler is not None):
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
    self.ReStart()
    self.SendFrame()
    self._wrapper.Run()

  @staticmethod
  def setupArgs(parser):
    Show.SetArgs(parser)
    PixelDisplay.SetArgs(parser)
    Relays.SetArgs(parser)
    PixelPatterns.SetArgs(parser)
    Sparkler.SetArgs(parser)

    
def main():
  parser = argparse.ArgumentParser()

  options = parser.parse_args()
  print "args are" , options
  show = Show(options)
  show.Run()


if __name__ == '__main__':
  main()
