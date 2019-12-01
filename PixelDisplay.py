import array
import random
from utils import *

class PixelDisplay(object):

  class Strand(object):
    # create strand of length pixels with prefix pixels not used (except for slide)
    # hold pixels of prefix remain until slide restarts
    # universe is starting universe
    # maxchannels is max channels per universe, universe increments by one past
    # buffer created is twice required length so slide is implemented by shifting window not by moving bits
    def __init__(self, wrapper, universe, length, prefix, hold, options, maxchannels=510):
      self._universe = universe
      self._maxchannels = maxchannels 
      self._channels = length * 3
      self._pixels = array.array('B', [0] * self._channels * 2)
      self._prefix = prefix
      self._hold = hold
      self._slid = 0
      self._drawable_length = length - prefix
      self._draw = True
      self._wrapper = wrapper
      self._options = options

    _zero_pixel = array.array('B', [0, 0, 0])

    # probably more pythonic to implement __len__
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

    def SlideLeft(self, finish = False):
      n = self._channels//3 - self._hold if not finish else self._hold
      for j in xrange(n):
        self._slid += 3
        self._draw = True
        yield True

    def SendDmx(self):
      if (self._draw):
        u = self._universe
        # copies horribly to spread across universes
        bases = xrange(0+self._slid, self._channels+self._slid, self._maxchannels)
        for b in bases:
          data = self._pixels[b: min(b+self._maxchannels, self._channels+self._slid)]
          self._wrapper.Client().SendDmx(u, data, DmxSent)
          u += 1
      self._draw = False
    
  def __init__(self, wrapper, options):
    self._draw = False
    self._wrapper = wrapper
    self._strands = []

    self._strands.append(PixelDisplay.Strand(wrapper, 1, 150, 48, 26, options))
    self._strands.append(PixelDisplay.Strand(wrapper, 2, 250, 18, 0, options))
    #self._strands.append(PixelDisplay.Strand(wrapper, 1, 150, 0, 0, options))
    #self._strands.append(PixelDisplay.Strand(wrapper, 2, 250, 0, 0, options))

    self._length = sum(map(lambda s: s.length, self._strands))
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
  def ColorSet(self, pixel, red, green, blue):
    (s, p) = pixel
    s.ColorSet(p, red, green, blue)

  # slide all strings left and return true/false if more to slide
  # implemented as generator so it looks like a normal loop
  def SlideLeft(self, finish = False):
    for s in self._strands:
      for p in s.SlideLeft(finish):
        yield True
    yield False # not pythonic, but we aren't calling it in a loop, either

  def SendDmx(self):
    for s in self._strands:
      s.SendDmx();
