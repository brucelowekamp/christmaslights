import array
import random
from Options import Options

class PixelDisplay(object):

  MaxBright = 0.50 # fraction of max pixel brightness to run at.  Not configurable
                   # as it's something of a safety issue: fuses will blow if set to 1
  
  # to deal with strand with unused segments mid-strand, create a class that maps
  # from drawable pixel i to strand pixel j
  class StrandMap(object):
    def __init__(self, length, prefix):
      self._length = length
      self._prefix = prefix
      self._map = [] # simply holds sequence of valid j's

      self._calc_map()
      
    # build the map for this strand, overridden by more complex implementations
    def _calc_map(self):
      self._map = range(self._prefix, self._length)
    
    @property
    def strand_len(self):
      return self._length

    # drawable length is length of map of j pixels
    def __len__(self):
      return len(self._map)

    # return iteration of j pixels
    def __iter__(self):
      return iter(xrange(self._drawable_length))

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
      return iter(xrange(len(self._map)))

    #return [R, G, B] of pixel
    def ColorGet(self, ipixel):
      pixel = self._map[ipixel]
      return [self._pixels[pixel*3+0], self._pixels[pixel*3+1],self._pixels[pixel*3+2]]

    def ColorSet(self, ipixel, red, green, blue):
      pixel = self._map[ipixel]
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

    @staticmethod
    def DmxSent(state):
      if not state.Succeeded():
        print ("Error: ", state.message)
        raise

    def SendDmx(self):
      if (self._draw):
        u = self._universe
        # copies horribly to spread across universes
        bases = xrange(0+self._slid, self._channels+self._slid, self._maxchannels)
        for b in bases:
          data = self._pixels[b: min(b+self._maxchannels, self._channels+self._slid)]
          # note: this is slow and non-pythonic, but would need to switch to numpy
          # array for anything reasonable to not return a list instead of array
          for i in xrange(len(data)):
            data[i] = int(data[i]*PixelDisplay.MaxBright)
          self._wrapper.Client().SendDmx(u, data, PixelDisplay.Strand.DmxSent)
          u += 1
      self._draw = False
    
  def __init__(self, wrapper):
    self._draw = False
    self._wrapper = wrapper
    self._strands = []

    self._strands.append(PixelDisplay.Strand(wrapper, 1, PixelDisplay.StrandMap(150, 48), 26))
    self._strands.append(PixelDisplay.Strand(wrapper, 2, PixelDisplay.StrandMap(250, 18), 0))
    #self._strands.append(PixelDisplay.Strand(wrapper, 1, PixelDisplay.StrandMap(150, 0), 0))
    #self._strands.append(PixelDisplay.Strand(wrapper, 2, PixelDisplay.StrandMap(250, 0), 0))

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
