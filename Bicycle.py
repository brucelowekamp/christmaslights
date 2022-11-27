import enum
import gc
import logging
import math
import random

from PixelPatterns import PixelPatterns

Black = (0, 0, 0)
RedLow = (10, 0, 0)
RedMedium = (100, 0, 0)
RedHigh = (255, 0, 0)
White = (255, 255, 255)

try:
  from ola.ClientWrapper import ClientWrapper
except ImportError:
  logging.warning("NO OLA INSTALLED!!!  USING STUB OLA!!!")
  from OLAStubClientWrapper import ClientWrapper

from Options import Options
from PixelDisplay import PixelDisplay
from PixelPatterns import PixelPatterns
import Ranges
from Sparkler import Sparkler

# to test: python3 Bicycle.py --pattern=HeatherStrand --wheel=80,40,2 --spinner=140-144,146-150:10,140,155,170,185 --bicycleranges=0-70,250
#
# Bicycle has three features.  The frame bits are normal pattern.  The
# wheels can be split into two bits: tires and spokes.  Tires (and
# chains) are simply a sequence that rotates in a circle, called wheel.  Spokes and
# crankset are referred to as spinners, where the line goes in a
# sequence.
#
# it's very important to lay out the tires so they move forward,
# ordered clockwise from the right side.  Same ordering with spokes,
# they move clockwise, going over one slot and back across the wheel
# so each spoke reverses.
#
# The strand range includes only the non-wheel bits of the bike.  The
# wheel and spinner generate their own colors from the colorset and
# have their own syntax to determine where to map.
class Bicycle(object):
  @staticmethod
  def SetArgs(parser):
    parser.add_argument('--bicycleuniverse', dest='bicycleuniverse', action='store', help="universe with bicycle on it", type=int, default=1)
    parser.add_argument('--bicycleranges', dest='bicycleranges', action='store', help="strand ranges for bicycle.  should include only first of each wheel/crank spinner include extra pixel  ", default='0-70,140-147,200')
    parser.add_argument('--wheel', dest='wheeldef', action='append', help="wheel start, length, pace", default=[]) # --wheel=80,51,1 --wheel=100,10,1
    parser.add_argument('--wheelfade', dest='wheelfade', type=float, default=3.5, help="exp scaling for wheel fade")

    parser.add_argument('--spinner', dest='spindef', action='append', help="<first spoke range>:pace, start, start, start, ...", default=[]) # --spinner=140-144,146-150:4,140,155,170,185

  class Wheel(object):
    def __init__(self, start, length, pace):
      self._start = start * 3
      self._length = length * 3
      self._pace = pace
      self._step = 0
      self._maxstep = pace * length

    def Animate(self, source, dest):
      self._step += 1
      if self._step >= self._maxstep:
        self._step = 0
      offset = self._step // self._pace
      # offset is in pixels, now need to handle color
      pixoff = offset * 3

      # these are copied from end to start
      copystart = self._start + self._length - pixoff
      for i in range(0, pixoff):
        dest[self._start + i] = source[copystart + i]

      # now copy from start to end
      for i in range(0, self._length - pixoff):
        dest[self._start + pixoff + i] = source[self._start + i]

  class Spinner(object):
    def __init__(self, length, pace, starts):
      self._starts = [s*3 for s in starts]
      self._spokes = len(starts)
      self._length = length * 3
      self._pace = pace
      self._step = 0
      self._maxstep = pace * self._spokes * 2
      self._isreverse = pace * self._spokes

    # spinner animation assumes spinners alernate in direction.  They
    # need to proceed in the forward direction, i.e. second one will
    # be animated next so should be rolling forward.  So take first
    # across, move clockwise and take next across.
    #
    # working out animation cycle as it spins each spoke alternates
    # direction.  Then go through them again in backward direction,
    # then start over.  So A fwd, B rev, C fwd, A rev, B fwd, C rev,
    # Afwd...
    def Animate(self, source, dest):
      self._step += 1
      if self._step >= self._maxstep:
        self._step = 0
      spokei = self._step // self._pace
      # we first iterate in normal direction then reverse
      spokei = spokei % self._spokes
      reverse = spokei % 2 == 1
      if self._step > self._isreverse:
        reverse = not reverse
        
      
      if spokei != 0 or (spokei == 0 and reverse):
        for i in range(0, self._length, 3):
          if not reverse:
            destindex = self._starts[spokei]+i
          else:
            destindex = self._starts[spokei] + self._length - 3 - i
          dest[destindex] = source[self._starts[0]+i]
          dest[destindex+1] = source[self._starts[0]+i+1]
          dest[destindex+2] = source[self._starts[0]+i+2]
          # wipe out first spoke
          if spokei != 0:
            dest[self._starts[0]+i] = 0
            dest[self._starts[0]+i+1] = 0
            dest[self._starts[0]+i+2] = 0
        
  def __init__(self, wrapper, pattern, onFinished):
    self._wrapper = wrapper
    self._onFinished = onFinished

    strandlist = f"PixelDisplay.Strand(wrapper, {Options.bicycleuniverse}, PixelDisplay.StrandMap(ranges=\"{Options.bicycleranges}\"), 0)"
    logging.debug(f"bicycle strandlist is {strandlist}")
    # source is what sparkler runs on for normal sparkle/flow
    self._sourcedisplay = PixelDisplay(wrapper, strandlist=[strandlist])
    self._sourcestrand = next(self._sourcedisplay.strands())
    # animate is what source is copied to with wheel and spinners
    self._animatedisplay = PixelDisplay(wrapper, strandlist=[strandlist])
    self._animatestrand = next(self._animatedisplay.strands())
    self._colorset = []
    self._sparkler = pattern(self._sourcedisplay, self._colorset)
    assert(len(self._colorset) > 1)
    self._stepcount = 0
    self._features = []
    source = self._sourcestrand.Raw()

    for w in Options.wheeldef:
      params = w.split(',')
      # start, length, pace
      start = int(params[0])
      length = int(params[1])
      pace = int(params[2])
      self._features.append(Bicycle.Wheel(start, length, pace))
      assert(length > 4)
      wheelfade = Options.wheelfade
      
      a = random.choice(self._colorset)
      b = a
      while (a == b):
        b = random.choice(self._colorset)
      
      for i in range(length):
        frac = 0
        if i < length / 2:
          frac = (length/2-i)/(length/2)
        else:
          frac = (i-length/2)/(length/2)
        scale = math.exp(frac * wheelfade - wheelfade)

        source[(start+i)*3] = int(scale * a[0] + (1-scale) * b[0])
        source[(start+i)*3+1] = int(scale * a[1] + (1-scale) * b[1])
        source[(start+i)*3+2] = int(scale * a[2] + (1-scale) * b[2])
        
        
      
    for s in Options.spindef:
      [rangestring,paramstring] = s.split(':')
      pixels = Ranges.Parse(rangestring)
      params = paramstring.split(',')
      # "pace, start, start, start, ..."
      length = pixels[-1]-pixels[0]+1
      pace = int(params.pop(0))
      starts = list(map(int, params))
      assert(starts[0] == pixels[0])
      a = random.choice(self._colorset)
      b = a
      while (length > 5 and a == b):
        b = random.choice(self._colorset)
      for i in range(length//2):
        pixel = pixels.pop(0)
        source[pixel*3] = a[0]
        source[pixel*3+1] = a[1]
        source[pixel*3+2] = a[2]
      while len(pixels) > 0:
        pixel = pixels.pop()
        source[pixel*3] = b[0]
        source[pixel*3+1] = b[1]
        source[pixel*3+2] = b[2]
      self._features.append(Bicycle.Spinner(length, pace,
                                            starts))
                                                                
  def Start(self):
    logging.info("Start")
    self._stepcount = 0

  def PedalTheBike(self):
    source = self._sourcestrand.Raw()
    animate = self._animatestrand.Raw()
    for i in range(len(source)):
      animate[i] = source[i]
    for w in self._features:
      w.Animate(source, animate)
    
  def AnimateNextFrame(self):
    self._animatedisplay.SendDmx()
    if self._sparkler is not None:
      self._sparkler.Sparkle()

    self.PedalTheBike()


  def _driver(self):
    # run loop for when used by itself without grinch show
    self.AnimateNextFrame()
    self._wrapper.AddEvent(50, lambda: self._driver())

  def _internalFinish(self):
    # used to shutdown when running by ourself
    self._wrapper.AddEvent(2000, lambda: self.Blackout())
    self._wrapper.AddEvent(2100, lambda: self._wrapper.Stop())

def main():
  Bicycle.SetArgs(Options.parser)
  Options.ParseArgs()
  print ("starting")
  wrapper = ClientWrapper()
  patterns = PixelPatterns()
  pattern = patterns.nextPattern()
  bicycle = Bicycle(wrapper, pattern, lambda: bicycle._internalFinish())
  wrapper.AddEvent(50, lambda: bicycle._driver())
  bicycle.Start()
  wrapper.Run()
  

if __name__ == '__main__':
  main()
