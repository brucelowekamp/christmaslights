import random

class Sparkler(object):
  def __init__(self, display, red, green, blue, steps, options):
    self._display = display
    self._Target = [red, green, blue]
    self._MaxStep = 0.1
    self._pixel = None
    self._Steps = steps
    self._onstep = 0
    self._curcolor = [0, 0, 0]
    self._options = options

  def Sparkle(self):
    if (self._pixel is None):
      strand = random.choice(list(self._display.strands())) # forgive me for I have sinned
      self._pixel = (strand, random.randrange(strand.length))
      self._orig = self._display.ColorGet(self._pixel)
      self._delta = [0, 0, 0]
      for i in xrange(3):
        self._delta[i] = (self._Target[i] - self._orig[i])/(self._Steps*1.0)
      self._onstep = int(self._Steps)
      self._curcolor = list(self._orig) # copy

    self._onstep -= 1
    pixel = self._pixel
    if (self._onstep > -1 * self._Steps):
      for i in xrange(3):
        if self._onstep > 0:
          self._curcolor[i] = self._curcolor[i] + self._delta[i]
        else:
          self._curcolor[i] = self._curcolor[i] - self._delta[i]

        if (int(self._curcolor[i]) < 0):
          self._curcolor[i] = 0
        elif (int(self._curcolor[i]) > 255):
          self._curcolor[i] = 255
          
    else:
      self._pixel = None
      self._curcolor = self._orig
    self._display.ColorSet(pixel, int(self._curcolor[0]), int(self._curcolor[1]), int(self._curcolor[2]))
      
      
