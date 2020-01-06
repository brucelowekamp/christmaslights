import math
from wl_to_rgb import wavelength_to_rgb
from Sparkler import Sparkler
import random
from Options import Options


# decorator to build list of pattern functions to call by name or by list
class pattern(object):
  byname = {}
  funcs = []

  def __init__(self, f):
    self._f = f
    pattern.byname[f.__name__] = self
    pattern.funcs.append(self)

  def __call__(self, *args):
    return self._f(*args)

  def __getattr__(self, attr):
    return getattr(self._f, attr)


class PixelPatterns(object):

  def __init__(self):
    self._showcount = 0
    self._pattern = None
    if (Options.pattern is not None):
      self._pattern = pattern.byname[Options.pattern]

  # set the next pattern in the show to run and return the sparkler (or none)
  def nextPattern(self, display):
    if (self._pattern is not None):
      doing = self._pattern
    else:
      doing = random.choice(pattern.funcs)
    self._showcount += 1
    return doing(display)

  @staticmethod
  def SetArgs(parser):
    parser.add_argument('--fademin', type=int, default=6, help="min side of exp in rgfade")
    parser.add_argument('--fadesets',
                        type=int,
                        default=5,
                        help="number of fadesets per strand in rgfade")
    parser.add_argument('--rgsize',
                        type=int,
                        default=5,
                        help="size of red/green blocks in RG pattern")
    parser.add_argument('--pattern',
                        type=str,
                        help="run only pattern, choose from " +
                        str([name for name in pattern.byname]))

  @staticmethod
  @pattern
  def RedGreen(display):
    print("RedGreen pattern")
    i = 0
    for p in display:
      red = (i // Options.rgsize) % 2 == 0
      display.ColorSet(p, 255 if red else 0, 0 if red else 255, 0)
      i += 1
    return Sparkler.Twinkle(display)

  @staticmethod
  # @pattern  # interesting idea, but not used at the moment
  def RGFade(display):
    print("RGFade pattern")
    minf = Options.fademin
    fadesets = Options.fadesets

    for s in display.strands():
      # break into fadesets segments and spread remainder out over first segments
      set_size = len(s) // fadesets
      remain = len(s) % fadesets
      blocks = [set_size] * fadesets
      for b in range(remain):
        blocks[b] += 1

      base = 0
      for set in range(fadesets):
        for pixel in range(blocks[set]):
          faded = int(math.exp((pixel + 1.0) / blocks[set] * minf - minf) * 255)
          red = faded if set % 2 == 0 else 0
          green = 0 if set % 2 == 0 else faded
          delta = pixel if set % 2 == 0 else set_size - pixel - 1
          s.ColorSet(base + delta, red, green, 0)
        base += blocks[set]
    return None

  @staticmethod
  @pattern
  def WhiteFlow(display):
    print("WhiteFlow")
    for p in display:
      display.ColorSet(p, 175, 175, 100)

    return Sparkler.FlowPulse(display, lambda: (0, 0, 255))

  # what we want to do is change the spectral rainbow to look more
  # evenly distributed colorwise to what humans think rainbows look like
  # so this was done by looking at the uniform spectral rainbow
  # (between 380 & 380+370nm) and calculating a mapping for that
  RainbowMap = [(0, 0),
                (1.0 / 7, 7.0 / 50),
                (2.0 / 7, 10.0 / 50),
                (3.0 / 7, 33.0 / 98),
                (4.0 / 7, 44.0 / 98),
                (5.0 / 7, 63.0 / 98),
                (6.0 / 7, 67.0 / 98),
                (1.0, 1.0)] # yapf:disable

  @staticmethod
  def FracToRainbow(x):
    assert (x >= 0 and x <= 1.0)
    if (x == 0):
      return 0
    i = 1
    while (x > PixelPatterns.RainbowMap[i][0]):
      i += 1

    x1 = PixelPatterns.RainbowMap[i - 1][0]
    y1 = PixelPatterns.RainbowMap[i - 1][1]
    x2 = PixelPatterns.RainbowMap[i][0]
    y2 = PixelPatterns.RainbowMap[i][1]

    y = (y2 - y1) / (x2 - x1) * (x - x2) + y2
    # print i, "map", x, y
    return y

  @staticmethod
  @pattern
  def Rainbow(display):
    print("Rainbow")
    for s in display.strands():
      l = len(s)
      for p in s:
        # (r, g, b) = colorsys.hsv_to_rgb((p*1.0)/l, 1, 1)
        # display.ColorSetStrand(s, p, int(r*255), int(g*255), int(b*255))
        x = (l - p - 1.0) / l
        x = PixelPatterns.FracToRainbow(x)
        (r, g, b) = wavelength_to_rgb(x * 370 + 380)
        s.ColorSet(p, r, g, b)
    return Sparkler.Twinkle(display)

  # heather wants a strand of red, green, blue, white, and purple
  HeathersColors = [(255, 0, 0),
                    (0, 255, 0),
                    (0, 0, 255),
                    (175, 175, 100),
                    (220, 0, 220)]  # yapf:disable

  @staticmethod
  def PickHeatherColor():
    return random.choice(PixelPatterns.HeathersColors)

  @staticmethod
  @pattern
  def HeatherStrand(display):
    print("RGBWP pattern")
    for p in display:
      color = PixelPatterns.PickHeatherColor()
      display.ColorSet(p, color[0], color[1], color[2])
    return Sparkler.FlowTo(display, PixelPatterns.PickHeatherColor)

  @staticmethod
  @pattern
  def RGFlow(display):
    print("RGFlow")
    for p in display:
      display.ColorSet(p, 255, 0, 0)
    return Sparkler.FlowPulse(display, lambda: (0, 255, 0))

  @staticmethod
  @pattern
  def RandomFlow(display):
    print("RandomFlow")
    a = PixelPatterns.PickHeatherColor()
    while True:
      b = PixelPatterns.PickHeatherColor()
      if (a != b):
        break
    for p in display:
      display.ColorSet(p, a[0], a[1], a[2])

    return Sparkler.FlowPulse(display, lambda: (b[0], b[1], b[2]))

  @staticmethod
  @pattern
  def RandomStrands(display):
    print("RandomStrands")
    colors = list(PixelPatterns.HeathersColors)
    random.shuffle(colors)
    for s in display.strands():
      a = colors.pop()
      for p in s:
        s.ColorSet(p, a[0], a[1], a[2])
    a = colors.pop()
    return Sparkler.FlowPulse(display, lambda: a)
