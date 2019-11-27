import random

class Sparkler(object):
  @staticmethod
  def SetArgs(parser):
    parser.add_argument('--sparkpct', type=float, default=0.02, help="proportion of pixels sparkling")

  
  def __init__(self, display, red, green, blue, steps, options, percent=None):
    self._display = display
    self._options = options
    self._Target = [red, green, blue]
    self._Steps = steps
    self._NumFlashers = int(( options.sparkpct if percent is None else percent)
                            * self._display.length)
    self._flashers = []
    self._being_flashed = set([])

  class Flasher(object):
    def __init__(self, pixel, color, target, steps):
      self._pixel = pixel
      self._onstep = int(steps)
      self._orig = color
      self._curcolor = list(color) #copy
      self._delta = [0, 0, 0]
      for i in xrange(3):
        self._delta[i] = (target[i] - self._orig[i])/(steps*1.0)


  def _add_flasher(self):
    while True:
      strand = random.choice(list(self._display.strands())) # forgive me for I have sinned
      pixel = (strand, random.randrange(strand.length))
      if (not pixel in self._being_flashed):
        break
    self._being_flashed.add(pixel)
    self._flashers.append(Sparkler.Flasher(pixel, self._display.ColorGet(pixel),
                                           self._Target, self._Steps))
    
    
  def Sparkle(self):
    if (len (self._flashers) < self._NumFlashers ):
      self._add_flasher()

    for flasher in self._flashers:
      flasher._onstep -= 1
      if (flasher._onstep > -1 * self._Steps):
        for i in xrange(3):
          if flasher._onstep >= 0:
            flasher._curcolor[i] = flasher._curcolor[i] + flasher._delta[i]
          else:
            flasher._curcolor[i] = flasher._curcolor[i] - flasher._delta[i]

          if (int(flasher._curcolor[i]) < 0):
            flasher._curcolor[i] = 0
          elif (int(flasher._curcolor[i]) > 255):
            flasher._curcolor[i] = 255
      else:
        flasher._curcolor = flasher._orig
      #print "step ", flasher._onstep, " colors", flasher._curcolor
      self._display.ColorSet(flasher._pixel, int(flasher._curcolor[0]), int(flasher._curcolor[1]), int(flasher._curcolor[2]))

      finished = filter(lambda f: f._onstep <= -1 * self._Steps, self._flashers)
      for f in finished:
        self._flashers.remove(f)
        self._being_flashed.remove(f._pixel)
        self._add_flasher()
      
