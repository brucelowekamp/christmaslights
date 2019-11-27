import random

class Sparkler(object):
  @staticmethod
  def SetArgs(parser):
    pass
  
  def __init__(self, display, red, green, blue, steps=4, fraction=0.02):
    self._display = display
    #self._options = options
    self._Target = [red, green, blue]
    self._Steps = steps
    self._NumFlashers = max(int(fraction * self._display.length), 1)
    self._flashers = []
    self._being_flashed = set([])

  class Flasher(object):
    def __init__(self, display, pixel, target, steps):
      self._display = display
      self._pixel = pixel
      self._onstep = int(steps)
      self._orig = self._display.ColorGet(pixel)
      self._curcolor = list(self._orig) #copy
      self._steps = steps
      self._delta = [0, 0, 0]
      for i in xrange(3):
        self._delta[i] = (target[i] - self._orig[i])/(steps*1.0)

    def flash(self):
      self._onstep -= 1
      if (self._onstep > -1 * self._steps):
        for i in xrange(3):
          if self._onstep >= 0:
            self._curcolor[i] = self._curcolor[i] + self._delta[i]
          else:
            self._curcolor[i] = self._curcolor[i] - self._delta[i]

          if (int(self._curcolor[i]) < 0):
            self._curcolor[i] = 0
          elif (int(self._curcolor[i]) > 255):
            self._curcolor[i] = 255
      else:
        self._curcolor = self._orig
      #print "step ", self._onstep, " colors", self._curcolor
      self._display.ColorSet(self._pixel, int(self._curcolor[0]), int(self._curcolor[1]), int(self._curcolor[2]))


  def _add_flasher(self):
    while True:
      pixel = self._display.random()
      if (not pixel in self._being_flashed):
        break
    self._being_flashed.add(pixel)
    self._flashers.append(Sparkler.Flasher(self._display, pixel,
                                           self._Target, self._Steps))
    
    
  def Sparkle(self):
    if (len (self._flashers) < self._NumFlashers ):
      self._add_flasher()

    for flasher in self._flashers:
      flasher.flash()
    finished = filter(lambda f: f._onstep <= -1 * self._Steps, self._flashers)
    for f in finished:
      self._flashers.remove(f)
      self._being_flashed.remove(f._pixel)
      self._add_flasher()
      
