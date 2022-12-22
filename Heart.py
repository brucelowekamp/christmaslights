import enum
import gc
import logging
import random

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

class Heart(object):
  @staticmethod
  def SetArgs(parser):
    parser.add_argument('--heartuniverse', dest='heartuniverse', action='store', help="universe with heart on it", type=int, default=15)
    parser.add_argument('--heartranges', dest='heartranges', action='store', help="ranges of strand for heart", default='0-29,30-74,75-125,126-182')
    parser.add_argument('--heartpace', dest='heartpace', action='store', type=int, help="cycles between heart changes", default='4')
    parser.add_argument('--heartsparkle', dest='heartsparkle', action='store', type=float, help="time to sparkle after flowing", default='2.5')

  def __init__(self, wrapper, onFinished):
    self._wrapper = wrapper
    self._onFinished = onFinished

    strandlist = f"PixelDisplay.Strand(wrapper, {Options.heartuniverse}, PixelDisplay.StrandMap(ranges=\"{Options.heartranges}\"), 0)"
    logging.debug(f"heart strandlist is {strandlist}")
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
    self._stepcount = 0
    
    logging.debug (f"config with {self._heartSlices}")
    # start black
    self.Blackout()


  # set heart #heart to color (r, g, b)
  def _setHeart(self, heart, color):
    (start, end) = self._heartSlices[heart]
    for p in range(start, end):
      self._strand.ColorSet(p, color[0], color[1], color[2])
      
  def Blackout(self):
    logging.debug("Blackout")
    for p in self._display:
      self._display.ColorSet(p, 0, 0, 0)

  # main animation of growing heart, as generator
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
    self._sparkler = Sparkler.Twinkle(self._display, colorfunc=lambda: random.choice([RedHigh, RedHigh,  White]), frac=0.25)
    self._wrapper.AddEvent(int(Options.heartsparkle*1000),
                           lambda: self._stop())

  def Start(self):
    logging.info("Start")
    self._stepcount = 0
    self.Blackout()
    self._animate = self._rollTo()

  def _stop(self):
    self._animate = None
    self._sparkler = None
    for h in range(len(self._heartSlices)):
      self._setHeart(h, RedMedium)
    self._wrapper.AddEvent(0, lambda: self._onFinished())
  
  def AnimateNextFrame(self):
    if Options.heartuniverse >= 0:
      self._display.SendDmx()
    if self._animate is not None and self._stepcount % Options.heartpace == 0:
      try:
        frame = next(self._animate)
        logging.debug (f"heart to {frame}")
        for h in range (len(self._heartSlices)):
          self._setHeart(h, frame[h])
      except StopIteration:
        self._animate = None
        self._sparkle()
    if self._sparkler is not None:
      self._sparkler.Sparkle()
    self._stepcount += 1

  def _driver(self):
    # run loop for when used by itself without grinch show
    self.AnimateNextFrame()
    self._wrapper.AddEvent(50, lambda: self._driver())

  def _internalFinish(self):
    # used to shutdown when running by ourself
    self._wrapper.AddEvent(2000, lambda: self.Blackout())
    self._wrapper.AddEvent(2100, lambda: self._wrapper.Stop())

def main():
  Heart.SetArgs(Options.parser)
  Options.ParseArgs()
  print ("starting")
  wrapper = ClientWrapper()
  heart = Heart(wrapper, lambda: heart._internalFinish())
  wrapper.AddEvent(50, lambda: heart._driver())
  heart.Start()
  wrapper.Run()
  

if __name__ == '__main__':
  main()
