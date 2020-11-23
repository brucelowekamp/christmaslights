import enum
import gc
import logging

Black = (0, 0, 0)
RedLow = (10, 0, 0)
RedMedium = (100, 0, 0)
RedHigh = (255, 0, 0)

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

class Heart(object):
  @staticmethod
  def SetArgs(parser):
    parser.add_argument('--heartuniverse', dest='heartuniverse', action='store', help="universe with heart on it", type=int, default=15)
    parser.add_argument('--heartranges', dest='heartranges', action='store', help="ranges of strand for heart", default='0-14,15-29,30-42,43-49')

  def __init__(self, wrapper, onFinished):
    self._wrapper = wrapper
    self._onFinished = onFinished

    strandlist = f"PixelDisplay.Strand(wrapper, {Options.heartuniverse}, PixelDisplay.StrandMap(ranges=\"{Options.heartranges}\"), 0)"
    logging.debug(f"strandlist is {strandlist}")
    self._display = PixelDisplay(wrapper, strandlist=[strandlist])
    lengths = Ranges.Parse(Options.heartranges, lengths=True)
    self._heartSlices = []
    start = 0
    for l in lengths:
      self._heartSlices.append( (start, start+l) )
      start += l
    self._strand = next(self._display.strands())
    self._animate = None
    self._sparkler = None
    
    logging.debug (f"config with {self._heartSlices}")
    # start black
    self._blackout()

    
  def _setHeart(self, heart, color):
    (start, end) = self._heartSlices[heart]
    logging.debug (f"from {start} to {end}")
    for p in range(start, end):
      self._strand.ColorSet(p, color[0], color[1], color[2])
      
  def _blackout(self):
    for p in self._display:
      self._display.ColorSet(p, 0, 0, 0)

  def _rollTo(self):
    def innerRollTo(total, goal):
      base = [Black]*total
      for i in range(0, goal):
        base[i] = RedMedium
      # yield base  # last frame from previous roll duplicates
      # roll H to become L
      for i in range(0, goal):
        resp = base.copy()
        resp[i] = RedHigh
        yield resp
      resp = base.copy()
      resp[goal] = RedLow
      yield resp
      base = resp.copy()

      # roll H to become M
      for i in range(0, goal):
        resp = base.copy()
        resp[i] = RedHigh
        yield resp
      resp = base.copy()
      resp[goal] = RedMedium
      yield resp

    total = len(self._heartSlices)
    for i in range(total):
      yield from innerRollTo(total, i)


  def _sparkle(self):
    self._sparkler = Sparkler.Twinkle(self._display, frac=0.25)
    self._wrapper.AddEvent(4000, lambda: self._stop())

  def _start(self):
    self._animate = self._rollTo()

  def Start(self):
    self._stepcount = 0
    self._blackout()
    self._wrapper.AddEvent(2000, lambda: self._start())
    self._wrapper.AddEvent(1, lambda: self.AnimateNextFrame())

  def _stop(self):
    self._animate = None
    self._sparkler = None
    self._blackout()
    self._wrapper.AddEvent(1000, lambda: self._onFinished())
  
  def AnimateNextFrame(self):
    self._display.SendDmx()
    if self._animate is not None and self._stepcount % 4 == 0:
      try:
        frame = next(self._animate)
        for h in range (len(self._heartSlices)):
          self._setHeart(h, frame[h])
      except StopIteration:
        self._animate = None
        self._wrapper.AddEvent(1000, lambda: self._sparkle())
    if self._sparkler is not None:
      self._sparkler.Sparkle()

    self._wrapper.AddEvent(50, lambda: self.AnimateNextFrame())
    self._stepcount += 1
    
def main():
  Heart.SetArgs(Options.parser)
  Options.ParseArgs()
  print ("starting")
  wrapper = ClientWrapper()
  heart = Heart(wrapper, lambda: wrapper.Stop())
  heart.Start()
  wrapper.Run()
  

if __name__ == '__main__':
  main()
