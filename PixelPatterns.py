import math
from wl_to_rgb import wavelength_to_rgb
import colorsys

class PixelPatterns(object):
  fade_min = 6
  options = None
  Patterns = None
  
  @staticmethod
  def SetArgs(parser):
    parser.add_argument('--fademin', type=int, default=6, help="min side of exp in rgfade")
    parser.add_argument('--fadesets', type=int, default=10, help="number of fadesets per strand in rgfade")
    parser.add_argument('--rgsize', type=int, default=5, help="size of red/green blocks in RG pattern")

  @staticmethod
  def SetOptions(options):
    PixelPatterns.options = options

  @staticmethod
  def RedGreen(display):
    print ("RedGreen pattern")
    i = 0
    for p in display:
      red = (i//PixelPatterns.options.rgsize)%2 == 0
      display.ColorSet(p, 255 if red else 0, 0 if red else 255, 0)
      i+=1

  @staticmethod
  def RGFade(display):
    print ("RGFade pattern")
    minf = PixelPatterns.options.fademin
    fadesets = PixelPatterns.options.fadesets
    
    for s in display.strands():
      # break into fadesets segments and spread remainder out over first segments
      set_size = s.length // fadesets
      remain = s.length % fadesets
      blocks = [set_size] * fadesets
      for b in range(remain):
        blocks[b] += 1

      base = 0
      for set in range(fadesets):
        for pixel in range(blocks[set]):
          faded = int(math.exp((pixel+1.0)/blocks[set]*minf-minf)*255)
          red = faded if set % 2 == 0 else 0
          green = 0 if set % 2 == 0 else faded
          delta = pixel if set % 2 == 0 else set_size - pixel - 1
          s.ColorSet(base + delta, red, green, 0)
        base += blocks[set]

  @staticmethod
  def White(display):
    print ("White")
    for p in display:
      display.ColorSet(p, 255, 255, 255)

  @staticmethod
  def Rainbow(display):
    print ("Rainbow")
    for s in display.strands():
      l = s.length
      for p in s:
        #(r, g, b) = colorsys.hsv_to_rgb((p*1.0)/l, 1, 1)
        #display.ColorSetStrand(s, p, int(r*255), int(g*255), int(b*255))
        (r, g, b) = wavelength_to_rgb((l-p-1.0)/l*370+380)
        s.ColorSet(p, r, g, b)

PixelPatterns.Patterns = [PixelPatterns.RedGreen, PixelPatterns.RGFade, PixelPatterns.White, PixelPatterns.Rainbow]
