import array
import random
from Options import Options
import Ranges
import unittest

class PixelDisplay(object):

  # Pixels at 100% brightness are too bright for nighttime displays.   We can run them
  # at a fraction of that for a good look and so we can wire fewer power injections.
  # Not configurable as it's something of a safety issue: fuses will blow if set to 1
  BrightFrac = 0.40 # fraction of max pixel brightness standard lights go at.  This can be
                    # overridden to support twinkling in Sparkler
  BrightSafety = 0.80 # assert if code tries to set average brightness different than this
  
  # to deal with strand with unused segments mid-strand, create a class that maps
  # from drawable pixel i to strand pixel j
  # input is length (total pixels) and prefix (number of dark pixels grinch can pull into)
  # or
  # range = range string ('25-50,60-99') of 0-based lit pixels.  length is assumed at last lit pixel
  class StrandMap(object):
    def __init__(self, length=None, prefix=None, ranges=None):
      assert((length is not None and prefix is not None and ranges is None) or
             (length is None and prefix is None and ranges is not None))
      if (ranges is None):
        self._length = length
        self._prefix = prefix
        self._map = range(self._prefix, self._length) # simply holds sequence of valid j's
      else:
        self._map = Ranges.Parse(ranges)
        self._length = max(self._map)+1
        self._prefix = min(self._map)
      
    @property
    def strand_len(self):
      return self._length

    # drawable length is length of map of j pixels
    def __len__(self):
      return len(self._map)

    # return iteration of j pixels
    def __iter__(self):
      return iter(range(self._drawable_length))

    # actual map
    def __getitem__(self, i):
      return self._map[i]

  class Strand(object):
    # create strand of strandmap pixels for drawing (except for slide)
    # hold pixels of prefix remain until slide restarts
    # universe is starting universe (these strands all start at channel 1)
    # maxchannels is max channels per universe, universe increments by one past
    # buffer created is twice required length so slide is implemented by shifting window not by moving bits
    def __init__(self, wrapper, universe, map, hold, maxchannels=510):
      self._universe = universe
      self._maxchannels = maxchannels 
      self._channels = map.strand_len * 3
      self._pixels = array.array('B', [0] * self._channels * 2)
      self._map = map
      self._hold = hold
      self._slid = 0
      self._draw = True
      self._wrapper = wrapper

    _zero_pixel = array.array('B', [0, 0, 0])

    def __len__(self):
      return len(self._map)

    # maybe it would be better to have pixels as a class, but no
    # do not expose the map aspect to consumers
    def __iter__(self):
      return iter(range(len(self._map)))

    #return [R, G, B] of pixel
    def ColorGet(self, ipixel):
      pixel = self._map[ipixel]
      return [self._pixels[pixel*3+0], self._pixels[pixel*3+1],self._pixels[pixel*3+2]]

    # set ipixel (index of drawable pixels) to colors
    # bypass if set does not reduce brightness automatically
    def ColorSet(self, ipixel, red, green, blue, bypass=False):
      pixel = self._map[ipixel]
      mult = PixelDisplay.BrightFrac if not bypass else 1
      self._pixels[pixel*3+0] = int(red * mult)
      self._pixels[pixel*3+1] = int(green * mult)
      self._pixels[pixel*3+2] = int(blue * mult)
      self._draw = True

    # returns a generator used to slide the pixels to the left.  Can be called twice, once slides to
    # hold pixels left (pixels grinch is holding in his hand) and the second time slides the rest of the
    # way.  Implemented by sliding a window to the right across the drawn pixels.
    def SlideLeft(self):
      slide_to = 3 * (self._map.strand_len - self._hold if self._slid == 0 else self._map.strand_len)
      while (self._slid < slide_to):
        if (self._map.strand_len <= 150):
          self._slid += 3
        else:
          self._slid += 6 # double rate for longer strands
        self._draw = True
        yield True

    @staticmethod
    def DmxSent(state):
      if not state.Succeeded():
        print ("Error: ", state.message)
        raise

    def SendDmx(self):
      if (self._draw):
        # check that average brightness isn't greater than BrightSafety of full on
        assert ( sum(self._pixels[self._slid:self._slid+self._channels])/self._channels <= 255*PixelDisplay.BrightSafety)
        u = self._universe
        # copies horribly to spread across universes
        bases = range(0+self._slid, self._channels+self._slid, self._maxchannels)
        for b in bases:
          data = self._pixels[b: min(b+self._maxchannels, self._channels+self._slid)]
          # note: this is slow and non-pythonic, but would need to switch to numpy
          # array for anything reasonable to not return a list instead of array
          self._wrapper.Client().SendDmx(u, data, PixelDisplay.Strand.DmxSent)
          u += 1
      self._draw = False
    
  def __init__(self, wrapper):
    self._draw = False
    self._wrapper = wrapper
    self._strands = []

    if not Options.inside:
      # grinch show outside
      self._strands.append(PixelDisplay.Strand(wrapper, 1, PixelDisplay.StrandMap(150, 48), 26))
      self._strands.append(PixelDisplay.Strand(wrapper, 2, PixelDisplay.StrandMap(ranges='55-110,141-349'), 22))
      self._strands.append(PixelDisplay.Strand(wrapper, 5, PixelDisplay.StrandMap(ranges='100-150,196-249'), 22))
    else:  # inside
      # family room
      self._strands.append(PixelDisplay.Strand(wrapper, 15, PixelDisplay.StrandMap(150, 0), 0))
      self._strands.append(PixelDisplay.Strand(wrapper, 17, PixelDisplay.StrandMap(350, 0), 0))

    self._length = sum(map(lambda s: len(s), self._strands))
    self._map = []
    for s in self._strands:
      for p in s:
        self._map.append( (s, p) )
        
  @staticmethod
  def SetArgs(parser):
    pass

  @property
  def length(self):
    return self._length
      
  @property
  def num_strands(self):
    return len(self._strands)

  # iterates across the map.  map tuples can be treated transparently and passed to ColorSet
  def __iter__(self):
    for s in self._strands:
      for p in s:
        yield (s, p)

  # iterate across the strands
  def strands(self):
    return iter(self._strands)

  # random pixel from across all pixels
  def random(self):
    return random.choice(self._map)
  
  #return [R, G, B] of pixel across all strands (by iterator)
  def ColorGet(self, pixel):
    (s, p) = pixel
    return s.ColorGet(p)

  # set pixel from global index to color ([ R, G, B ])
  # bypass standard brightness reduction if set
  def ColorSet(self, pixel, red, green, blue, bypass=False):
    (s, p) = pixel
    s.ColorSet(p, red, green, blue, bypass)

  # slide all strings left and return true/false if more to slide
  # implemented as generator so it looks like a normal loop to caller
  def SlideLeft(self):
    for s in self._strands:
      for p in s.SlideLeft():
        yield True
    yield False # not pythonic, but we aren't calling it in a loop, either

  def SendDmx(self):
    for s in self._strands:
      s.SendDmx();

class TestStrandMap(unittest.TestCase):
  def test_single(self):
    s = PixelDisplay.StrandMap(length=10,prefix=5)
    self.assertEqual(s.strand_len, 10)
    self.assertEqual(len(s), 5)
    self.assertEqual(s._map, [5,6,7,8,9])

  def test_single_range(self):
    s = PixelDisplay.StrandMap(ranges='5-9')
    self.assertEqual(s.strand_len, 10)
    self.assertEqual(len(s), 5)
    self.assertEqual(s._map, [5,6,7,8,9])

  def test_complex_strand(self):
    s = PixelDisplay.StrandMap(ranges='5-9,11,15-19')
    self.assertEqual(s.strand_len, 20)
    self.assertEqual(len(s), 11)
    self.assertEqual(s._map, [5,6,7,8,9,11,15,16,17,18,19])

if __name__ == '__main__':
  unittest.main()
