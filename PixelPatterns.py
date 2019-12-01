import math
from wl_to_rgb import wavelength_to_rgb
import colorsys
from Sparkler import *

class PixelPatterns(object):
  fade_min = 6
  options = None
  Patterns = None
  
  @staticmethod
  def SetArgs(parser):
    parser.add_argument('--fademin', type=int, default=6, help="min side of exp in rgfade")
    parser.add_argument('--fadesets', type=int, default=10, help="number of fadesets per strand in rgfade")
    parser.add_argument('--rgsize', type=int, default=5, help="size of red/green blocks in RG pattern")
    parser.add_argument('--sparkfrac', type=float, default=0.008, help="proportion of pixels sparkling")
    parser.add_argument('--flowfrac', type=float, default=0.5, help="proportion of pixels in flow")
    parser.add_argument('--sparksteps', type=int, default=2, help="steps up then down in spark")
    parser.add_argument('--flowsteps', type=float, default=15, help="steps up then down in flow")
    

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
    return Sparkler(display, 255, 255, 255, PixelPatterns.options.sparksteps, PixelPatterns.options.sparkfrac)
  
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
    return None

  @staticmethod
  def White(display):
    print ("White")
    for p in display:
      display.ColorSet(p, 175, 175, 100)

    return Sparkler(display, 0, 0, 255, PixelPatterns.options.flowsteps, PixelPatterns.options.flowfrac)

  # what we want to do is change the spectral rainbow to look more
  # evenly distributed colorwise to what humans think rainbows look like
  # so this was done by looking at the uniform spectral rainbow
  # (between 380 & 380+370nm) and calculating a mapping for that
  RainbowMap = [
    (0,0),
    (1.0/7, 7.0/50),
    (2.0/7, 10.0/50),
    (3.0/7, 33.0/98),
    (4.0/7, 44.0/98),
    (5.0/7, 63.0/98),
    (6.0/7, 67.0/98),
    (1.0, 1.0)
  ]
  @staticmethod
  def FracToRainbow(x):
    assert (x>= 0 and x <= 1.0)
    if (x == 0): return 0
    i = 1
    while (x > PixelPatterns.RainbowMap[i][0]):
      i += 1

    x1 = PixelPatterns.RainbowMap[i-1][0]
    y1 = PixelPatterns.RainbowMap[i-1][1]
    x2 = PixelPatterns.RainbowMap[i][0]
    y2 = PixelPatterns.RainbowMap[i][1]
    
    y = (y2 - y1)/(x2 - x1) * (x - x2) + y2
    #print i, "map", x, y
    return y
  
  @staticmethod
  def Rainbow(display):
    print ("Rainbow")
    for s in display.strands():
      l = s.length
      for p in s:
        #(r, g, b) = colorsys.hsv_to_rgb((p*1.0)/l, 1, 1)
        #display.ColorSetStrand(s, p, int(r*255), int(g*255), int(b*255))
        x = (l-p-1.0)/l
        x = PixelPatterns.FracToRainbow(x)
        (r, g, b) = wavelength_to_rgb(x*370+380)
        s.ColorSet(p, r, g, b)
    return Sparkler(display, 255, 255, 255, PixelPatterns.options.sparksteps, PixelPatterns.options.sparkfrac)

  @staticmethod
  def RGFlow(display):
    print ("RGFlow")
    for p in display:
      display.ColorSet(p, 255, 0, 0)
    return Sparkler(display, 0, 255, 0, PixelPatterns.options.flowsteps, PixelPatterns.options.flowfrac)

PixelPatterns.Patterns = [PixelPatterns.RedGreen, PixelPatterns.RGFade, PixelPatterns.White, PixelPatterns.Rainbow, PixelPatterns.RGFlow]
