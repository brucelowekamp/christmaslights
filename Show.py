try:
  from ola.ClientWrapper import ClientWrapper
except ImportError:
  print "NO OLA INSTALLED!!!  USING STUB OLA!!!"
  from OLAStubClientWrapper import ClientWrapper
from PixelDisplay import PixelDisplay
from PixelPatterns import PixelPatterns
from Relays import Relays
from Sparkler import Sparkler
from GrinchShow import *
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
    self._options = options
    PixelPatterns.SetOptions(options)
    self._wrapper = ClientWrapper()
    self._showcount = 0
    
    self._loop_count = 0
    self._relays = None
    self._display = None
    self._sliding = None
    self._target_time = time.time()

  @staticmethod
  def SetArgs(parser):
    parser.add_argument('--ondelay', type=int, default=3, help="delay between grinch sleigh appear and lights on")
    parser.add_argument('--grinchoffdelay', type=int, default=2, help="delay between grinch sleigh appear and lights turning off")
    parser.add_argument('--startslide', type=int, default=35, help="start grinch slide at seconds")
    parser.add_argument('--darktime', type=int, default=6, help="time to remain dark after slide before reset")
    parser.add_argument('--pattern', type=int, help="run only pattern index i")
    parser.add_argument('--nosleigh', action='store_true', help="no grinch sleigh for high winds")

  @property
  def options(self):
    return self._options

  def Start(self):
    print "START"
    self._loop_count = 0
    self._sliding = None
    self._display = PixelDisplay(self._wrapper, self._options)
    self._relays = Relays(self._wrapper, self._options)
    self._sparkler = None

    self.LoadTimings(GrinchShowStart(self._options))
                   
  def StartGrinch(self):
    print "GRINCH"
    self.LoadTimings(GrinchShowAppear(self._options))
    
  def EndGrinch(self):
    print "GRINCHGOING"
    self.LoadTimings(GrinchFinished(self._options))
   
  def StartSlide(self):
    print "start slide"
    gc.collect()
    self._sliding = self._display.SlideLeft()
    self._finished = False

  def FinishSlide(self):
    print "finish slide"
    gc.collect()
    self._sliding = self._display.SlideLeft(True)
    self._finished = True
    
  def NewDisplay(self):
    gc.collect()
    if (self._options.pattern is not None):
      pattern = PixelPatterns.Patterns[self._options.pattern]
    else:
      pattern = PixelPatterns.Patterns[self._showcount % len(PixelPatterns.Patterns)]
      self._showcount += 1
    self._sparkler = pattern(self._display)

  def LoadTimings(self, events):
    #print "adding events", events
    for e in events:
      ms = int(e[0] * 1000)
      if (self._options.nosleigh and len(e) == 3):
        if (e[2] == Relay.GRINCH_SLEIGH_FAN): e = (e[0], e[1], Relay.GRINCH_FAN)
        elif (e[2] == Relay.GRINCH_SLEIGH): e = (e[0], e[1], Relay.GRINCH)
      # switch... oh yeah
      if (e[1] == Commands.ON):
        self._wrapper.AddEvent(ms, lambda x=e[2]: self._relays.on(x))
      elif (e[1] == Commands.OFF):
        self._wrapper.AddEvent(ms, lambda x=e[2]: self._relays.off(x))
      elif (e[1] == Commands.START_GRINCH):
        self._wrapper.AddEvent(ms, lambda: self.StartGrinch())
      elif (e[1] == Commands.PIXELS_ON):
        self._wrapper.AddEvent(ms, lambda: self.NewDisplay())
      elif (e[1] == Commands.FINISH_SLIDE):
        self._wrapper.AddEvent(ms, lambda: self.FinishSlide())
      elif (e[1] == Commands.RESTART):
        self._wrapper.AddEvent(ms, lambda: self.Start())
      elif (e[1] == Commands.START_SLIDE):
        self._wrapper.AddEvent(ms, lambda: self.StartSlide())
        
  # send frame precomputed last call, then compute frame and schedule next call
  def SendFrame(self):
    # send (if pending), do first thing to time as precisely as we can
    self._display.SendDmx()
    self._relays.SendDmx()
    if (self._loop_count % (TICK_PER_SEC*10) == 0):
      print "loop: ", self._loop_count // TICK_PER_SEC
    
    if (self._sliding is not None):
      if (not self._sliding.next()):
        self._sliding = None
        if (not self._finished):
          # schedule final scene after first slide finishes
          self.EndGrinch()
        else:
          # after final slideoff and disappear, stop sparkling
          self._sparkler = None

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
    self.Start()
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
