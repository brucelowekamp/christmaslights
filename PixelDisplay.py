import array
from utils import *

class PixelDisplay(object):

  class Strand(object):
    # create strand of length pixels with prefix pixels not used (except for slide)
    # universe is starting universe
    # maxchannels is max channels per universe, universe increments by one past
    def __init__(self, wrapper, universe, length, prefix, options, maxchannels=510):
      self._universe = universe
      self._maxchannels = maxchannels 
      self._channels = length * 3
      self._pixels = array.array('B', [0] * self._channels)
      self._prefix = prefix
      self._drawable_length = length - prefix
      self._draw = False
      self._wrapper = wrapper
      self._options = options

    _zero_pixel = array.array('B', [0, 0, 0])

    @property
    def length(self):
      return self._drawable_length

    # maybe it would be better to have pixels as a class, but no
    def __iter__(self):
      return iter(xrange(self._drawable_length))

    #return [R, G, B] of pixel
    def ColorGet(self, pixel):
      assert pixel < self._drawable_length
      pixel += self._prefix
      return [self._pixels[pixel*3+0], self._pixels[pixel*3+1],self._pixels[pixel*3+2]]

    def ColorSet(self, pixel, red, green, blue):
      assert pixel < self._drawable_length
      pixel += self._prefix
      self._pixels[pixel*3+0] = red
      self._pixels[pixel*3+1] = green
      self._pixels[pixel*3+2] = blue
      self._draw = True

    def SlideLeft(self):
      for j in xrange(self._channels//3):
        del self._pixels[0:3]
        self._pixels.extend(PixelDisplay.Strand._zero_pixel)
        self._draw = True
        yield True

    def SendDmx(self):
      if (self._draw):
        u = self._universe
        bases = xrange(0, self._channels, self._maxchannels)
        for b in bases:
          data = self._pixels[b: min(b+self._maxchannels, self._channels)]
          self._wrapper.Client().SendDmx(u, data, DmxSent)
          u += 1
      self._draw = False
    
  def __init__(self, wrapper, options):
    self._draw = False
    self._wrapper = wrapper
    self._strands = []
    #self._strands.append(PixelDisplay.Strand(wrapper, 1, 150, 0, options, 300))
    self._strands.append(PixelDisplay.Strand(wrapper, 1, 100, 0, options))
    self._strands.append(PixelDisplay.Strand(wrapper, 2, 50, 0, options))
    self._length = sum(map(lambda s: s.length, self._strands))

  @staticmethod
  def SetArgs(parser):
    None

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

  #return [R, G, B] of pixel across all strands (by iterator)
  def ColorGet(self, pixel):
    (s, p) = pixel
    return s.ColorGet(p)

  # set pixel from global index to color ([ R, G, B ])
  def ColorSet(self, pixel, red, green, blue):
    (s, p) = pixel
    s.ColorSet(p, red, green, blue)

  # slide all strings left and return true/false if more to slide
  # implemented as generator so it looks like a normal loop
  def SlideLeft(self):
    for s in self._strands:
      for p in s.SlideLeft():
        yield True
    yield False # not pythonic, but we aren't calling it in a loop, either

  def SendDmx(self):
    for s in self._strands:
      s.SendDmx();
