import array
from utils import *

class PixelDisplay(object):

  def __init__(self, wrapper, options):
    self._draw = False
    self._num_strands = 2
    self._strand_length = [100, 50]
    self._strand_universe = [1, 2]
    self._pixels= [ None ] * self._num_strands
    for i in range(self._num_strands):
      self._pixels[i] = array.array('B', [0] * (3 * self._strand_length[i]))
    self._slide_remaining = max(self._strand_length)
    self._map = [] # tuples for all pixels of (strand_n, pixel_n )
    for i in range(self._num_strands):
      for j in range (self._strand_length[i]):
        self._map.append( (i , j ) )
    self._wrapper = wrapper
    self._zero_pixel = array.array('B', [0, 0, 0])

  @staticmethod
  def SetArgs(parser):
    None

  @property
  def length(self):
    return len(self._map)
      
  @property
  def num_strands(self):
    return self._num_strands

  @property
  def max_strand_length(self):
    return max(self._strand_length)

  @property
  def draw_pending(self):
    return self._draw
  
  # return length of strand
  def StrandLength(self, strand):
    assert strand < self._num_strands
    return self._strand_length[strand]

  # iterates across the map.  map tuples can be treated transparently and passed to ColorSet
  def __iter__(self):
    return iter(self._map)
  
  #return [R, G, B] of pixel from global index
  def ColorGet(self, pixel):
    (s, p) = pixel
    return self._pixels[s][p*3+0], self._pixels[s][p*3+1],self._pixels[s][p*3+2]

  #return [R, G, B] of pixel (0-based) on strand
  def ColorGetStrand(self, strand, pixel):
    assert strand < self._num_strands
    assert pixel < self._strand_length[strand]
    return self._pixels[strand][pixel*3+0], self._pixels[strand][pixel*3+1],self._pixels[strand][pixel*3+2]

  # set pixel from global index to color ([ R, G, B ])
  def ColorSet(self, pixel, red, green, blue):
    (s, p) = pixel
    self._pixels[s][p*3+0] = red
    self._pixels[s][p*3+1] = green
    self._pixels[s][p*3+2] = blue
    self._draw = True

  # set pixel on strand to color ([ R, G, B ])
  def ColorSetStrand(self, strand, pixel, red, green, blue):
    assert strand < self._num_strands
    assert pixel < self._strand_length[strand]
    self._pixels[strand][pixel*3+0] = red
    self._pixels[strand][pixel*3+1] = green
    self._pixels[strand][pixel*3+2] = blue
    self._draw = True

  # slide all strings left and return true/false if more to slide
  def SlideLeft(self):
    if (self._slide_remaining > 0):
      for i in range(self._num_strands):
        del self._pixels[i][0:3]
        self._pixels[i].extend(self._zero_pixel)
      self._slide_remaining -= 1
      self._draw = True
    return self._slide_remaining > 0

  def SendDmx(self):
    if (self._draw):
      for i in range(self._num_strands):
        self._wrapper.Client().SendDmx(self._strand_universe[i], self._pixels[i], DmxSent)
      self._draw = False
