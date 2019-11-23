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

  @staticmethod
  def SetOptions(options):
    PixelPatterns.options = options

  @staticmethod
  def RedGreen(display):
    print ("RedGreen pattern")
    i = 0
    for p in display:
      red = (i//5)%2 == 0
      display.ColorSet(p, 255 if red else 0, 0 if red else 255, 0)
      i+=1

  @staticmethod
  def RGFade(display, min_fade=6, num_sets=10):
    print ("RGFade pattern")
    minf = PixelPatterns.options.fademin
    
    for s in range(display.num_strands):

      set_size = display.StrandLength(s)//PixelPatterns.options.fadesets

      for set in range(num_sets):
        base = set * set_size
        color = set % 2

        for pixel in range(set_size):
          #print (int(math.exp((pixel+1.0)/set_size*6-6)*255))
          faded = int(math.exp((pixel+1.0)/set_size*minf-minf)*255)
          red = faded if set % 2 == 0 else 0
          green = 0 if set % 2 == 0 else faded
          delta = pixel if set % 2 == 0 else set_size - pixel - 1
          display.ColorSetStrand(s, base + delta, red, green, 0) 

  @staticmethod
  def White(display):
    print ("White")
    for p in display:
      display.ColorSet(p, 255, 255, 255)

  @staticmethod
  def Rainbow(display):
    print ("Rainbow")
    for s in range(display.num_strands):
      l = display.StrandLength(s)
      for p in range(l):
        #(r, g, b) = colorsys.hsv_to_rgb((p*1.0)/l, 1, 1)
        #display.ColorSetStrand(s, p, int(r*255), int(g*255), int(b*255))
        (r, g, b) = wavelength_to_rgb((l-p-1.0)/l*370+380)
        display.ColorSetStrand(s, p, r, g, b)

PixelPatterns.Patterns = [PixelPatterns.RedGreen, PixelPatterns.RGFade, PixelPatterns.White, PixelPatterns.Rainbow]
