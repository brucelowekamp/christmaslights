import enum
import gc

try:
  from ola.ClientWrapper import ClientWrapper
except ImportError:
  print("NO OLA INSTALLED!!!  USING STUB OLA!!!")
  from OLAStubClientWrapper import ClientWrapper

from Options import Options
from PixelDisplay import PixelDisplay
from PixelPatterns import PixelPatterns
import Ranges

Red = [255, 0, 0]

class Heart(object):
  @staticmethod
  def SetArgs(parser):
    parser.add_argument('--heartuniverse', dest='heartuniverse', action='store', help="universe with heart on it", type=int, default=15)
    parser.add_argument('--heartranges', dest='heartranges', action='store', help="ranges of strand for heart", default='0-9,15-24,30-39,45-49')

  def __init__(self, wrapper, onFinished):
    self._wrapper = wrapper
    self._onFinished = onFinished

    
    self._display = PixelDisplay(wrapper,
                                 strandlist=[f"PixelDisplay.Strand(wrapper, {Options.heartuniverse}, PixelDisplay.StrandMap(ranges=\"{Options.heartranges}\"), 0)"])
    lengths = Ranges.Parse(Options.heartranges, lengths=True)
    self._heartSlices = []
    start = 0
    for l in lengths:
      self._heartSlices.append( (start, start+l) )
      start += l
    self._strand = next(self._display.strands())

    print (f"config with {self._heartSlices}")
    # start black
    self._blackout()

    
  def _setHeart(self, heart, color):
    (start, end) = self._heartSlices[heart]
    print (f"from {start} to {end}")
    for p in range(start, end):
      self._strand.ColorSet(p, color[0], color[1], color[2])
      
  def _blackout(self):
    for p in self._display:
      self._display.ColorSet(p, 0, 0, 0)


  def _heartTiming(self, secs, heart, color):
    print(f"at {secs} set {heart} to {color}")
    self._wrapper.AddEvent(int(secs*1000),
                           lambda h=heart,c=color: self._setHeart(h, c) )
    
  def Start(self):
    self._heartTiming(1, 0, Red)
    self._heartTiming(2, 1, Red)
    self._heartTiming(3, 2, Red)
    self._heartTiming(4, 3, Red)
    self._wrapper.AddEvent(5*1000, lambda: self._blackout())
    self._wrapper.AddEvent(int(5.1*1000), lambda: self._onFinished())
    self._wrapper.AddEvent(0.05, lambda: self.AnimateNextFrame())
  
  def AnimateNextFrame(self):
    self._display.SendDmx()
    self._wrapper.AddEvent(0.05, lambda: self.AnimateNextFrame())
    
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
