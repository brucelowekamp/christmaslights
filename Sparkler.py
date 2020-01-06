import math
from Options import Options


def WhiteColor():
  return (255, 255, 255)


# sparkler is used to twinkle (flash white), to flow (slowly change to a color and back)
# and to permanently change to a new color
class Sparkler(object):

  @staticmethod
  def SetArgs(parser):
    parser.add_argument('--sparkfrac',
                        type=float,
                        default=0.002,
                        help="proportion of pixels sparkling")
    parser.add_argument('--flowfrac', type=float, default=0.5, help="proportion of pixels in flow")
    parser.add_argument('--sparksteps', type=int, default=2, help="steps up then down in spark")
    parser.add_argument('--flowsteps', type=int, default=15, help="steps up then down in flow")

  # FlowTo is a factory for a Sparkler that slowly transitions to a new color
  @staticmethod
  def FlowTo(display, colorfunc, steps=None, frac=None):
    return Sparkler(display,
                    colorfunc,
                    steps=(steps or Options.flowsteps),
                    fraction=(frac or Options.flowfrac),
                    reverse=False,
                    fullBright=False)

  # FlowPulse is a factory for a Sparkler that slowly transitions to an alt color and then back
  @staticmethod
  def FlowPulse(display, colorfunc, steps=None, frac=None):
    return Sparkler(display,
                    colorfunc,
                    steps=(steps or Options.flowsteps),
                    fraction=(frac or Options.flowfrac),
                    reverse=True,
                    fullBright=False)

  # twinkle is a factory for a Sparkler that randomly flashes quickly to white and back
  @staticmethod
  def Twinkle(display, colorfunc=None, steps=None, frac=None):
    return Sparkler(display, (colorfunc or WhiteColor),
                    steps=(steps or Options.sparksteps),
                    fraction=(frac or Options.sparkfrac),
                    reverse=True,
                    fullBright=True)

  # display is the overall PixelDisplay
  # colorfunc returns the color to change to
  # reverse indicates to go back
  # steps is how long to take (in each direction for reversing functions)
  # fraction is fraction of pixels in display to be changing at any one time
  # fullbright says to ignore the brightness cap and go to 100% (currently only used for twinkle white)
  def __init__(self, display, colorfunc, steps=4, fraction=0.02, reverse=True, fullBright=False):
    self._display = display
    self._Colorfunc = colorfunc
    self._Steps = steps
    self._reverse = reverse
    self._NumFlashers = max(int(fraction * self._display.length), 1)
    self._flashers = []
    self._being_flashed = set([])
    assert (not fullBright or reverse)
    self._fullBright = fullBright

  class Flasher(object):

    def __init__(self, display, pixel, colorfunc, steps, reverse, fullBright):
      from PixelDisplay import PixelDisplay

      self._display = display
      self._pixel = pixel
      self._onstep = int(steps)
      self._orig = self._display.ColorGet(pixel)
      self._curcolor = list(self._orig)  # copy
      self._steps = steps
      self._reverse = reverse
      self._done = False
      self._delta = [0, 0, 0]
      self._fullBright = fullBright
      target = list(colorfunc())
      for i in range(3):
        if (not fullBright):
          target[i] *= PixelDisplay.BrightFrac
        self._delta[i] = (target[i] - self._orig[i]) / (steps * 1.0)

    @property
    def done(self):
      return self._done

    def flash(self):
      self._onstep -= 1
      if ((self._reverse and (self._onstep > -1 * self._steps))
          or (not self._reverse and (self._onstep >= 0))):
        for i in range(3):
          if self._onstep >= 0:
            self._curcolor[i] = self._curcolor[i] + self._delta[i]
          else:
            self._curcolor[i] = self._curcolor[i] - self._delta[i]

          # in case rounding makes us a bit off, set to limits
          if (int(self._curcolor[i]) < 0):
            self._curcolor[i] = 0
          elif (int(self._curcolor[i]) > 255):
            self._curcolor[i] = 255
      else:
        if (self._reverse):
          self._curcolor = self._orig
        self._done = True

      # print "step ", self._onstep, "pixel", self._pixel[1], "colors", self._curcolor
      self._display.ColorSet(self._pixel,
                             int(self._curcolor[0]),
                             int(self._curcolor[1]),
                             int(self._curcolor[2]),
                             bypass=True)

  # distribute flasher start times over the period they recycle
  def _add_flashers(self):
    # round up to make sure we do something
    addpercall = int(math.ceil(self._NumFlashers / (self._Steps *
                                                    (2.0 if self._reverse else 1.0))))
    if (addpercall + len(self._flashers) > self._NumFlashers):
      addpercall = self._NumFlashers - len(self._flashers)
    for i in range(addpercall):
      self._add_flasher()

  def _add_flasher(self):
    while True:
      pixel = self._display.random()
      if (pixel not in self._being_flashed):
        break
    self._being_flashed.add(pixel)
    self._flashers.append(
        Sparkler.Flasher(self._display, pixel, self._Colorfunc, self._Steps, self._reverse,
                         self._fullBright))

  def Sparkle(self):
    if (len(self._flashers) < self._NumFlashers):
      self._add_flashers()

    for flasher in self._flashers:
      flasher.flash()
    finished = filter(lambda f: f.done, self._flashers)
    for f in finished:
      self._flashers.remove(f)
      self._being_flashed.remove(f._pixel)
