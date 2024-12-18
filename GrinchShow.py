import enum
import gc
import random

from Heart import Heart
from Options import Options
from Show import Show


class GrinchShow(Show):

  def __init__(self):
    super(GrinchShow, self).__init__()
    self._heart = Heart(self._wrapper, lambda: self.RestoreLights())
    self._sliding = None

  @staticmethod
  def SetArgs(parser):
    parser.add_argument('--ondelay',
                        type=int,
                        default=1,
                        help="delay between grinch sleigh appear and lights on")
    parser.add_argument('--grinchoffdelay',
                        type=int,
                        default=3,
                        help="delay between grinch sleigh appear and lights turning off")
    parser.add_argument('--darktime',
                        type=int,
                        default=3,
                        help="time to remain dark after slide before reset")
    parser.add_argument('--grinchprob',
                        type=float,
                        default=0.40,
                        help="Prob (e.g. 0.50) that grinch will appear, else new pattern")

  # commands used by Grinch animation
  class GrinchCommands(enum.Enum):
    START_GRINCH = 1  # grinch appears in his sleigh and steals the lights
    START_SLIDE = 2  # grinch begins pulling the lights (pixels) off the house
    FINISH_SLIDE = 3  # grinch is now finished (has coil of lights) so slide them off too
    START_HEART = 4  # run heart growing animation
    HEART_OFF = 5  # blackout heart
    PIXEL_SHOW = 6 # next pixel show and decide if doing grinch
    BIKE_OFF = 7 # blackout bike

  def LoadTiming(self, e):
    if (isinstance(e[1], GrinchShow.GrinchCommands)):
      ms = int(e[0] * 1000)
      # switch... oh yeah
      if (e[1] == GrinchShow.GrinchCommands.START_GRINCH):
        self._wrapper.AddEvent(ms, lambda: self.StartGrinch())
      elif (e[1] == GrinchShow.GrinchCommands.START_SLIDE):
        self._wrapper.AddEvent(ms, lambda: self.StartSlide())
      elif (e[1] == GrinchShow.GrinchCommands.FINISH_SLIDE):
        self._wrapper.AddEvent(ms, lambda: self.FinishSlide())
      elif (e[1] == GrinchShow.GrinchCommands.START_HEART):
        self._wrapper.AddEvent(ms, lambda: self._heart.Start())
      elif (e[1] == GrinchShow.GrinchCommands.HEART_OFF):
        self._wrapper.AddEvent(ms, lambda: self._heart.Blackout())
      elif (e[1] == GrinchShow.GrinchCommands.PIXEL_SHOW):
        self._wrapper.AddEvent(ms, lambda: self.PixelShow())
      elif (e[1] == GrinchShow.GrinchCommands.BIKE_OFF):
        self._wrapper.AddEvent(ms, lambda: self._bicycle.Blackout())
      else:
        raise NotImplementedError(e)
    else:
      super(GrinchShow, self).LoadTiming(e)

  @staticmethod
  # sequence of events that flashes on a relay r starting at time t
  def FlashOn(t, r):
    return [(t, Show.Commands.ON, r),
            (t + 0.05, Show.Commands.OFF, r),
            (t + 0.20, Show.Commands.ON, r),
            (t + 0.25, Show.Commands.OFF, r),
            (t + 0.30, Show.Commands.ON, r),
            (t + 0.40, Show.Commands.OFF, r),
            (t + 0.50, Show.Commands.ON, r),
            (t + 0.55, Show.Commands.OFF, r),
            (t + 0.60, Show.Commands.ON, r)] #yapf:disable

  @staticmethod
  # sequence of events that flashes off a relay r starting at time t
  def FlashOff(t, r):
    return [(t, Show.Commands.OFF, r),
            (t + 0.05, Show.Commands.ON, r),
            (t + 0.15, Show.Commands.OFF, r),
            (t + 0.20, Show.Commands.ON, r),
            (t + 0.30, Show.Commands.OFF, r),
            (t + 0.40, Show.Commands.ON, r),
            (t + 0.45, Show.Commands.OFF, r),
            (t + 0.55, Show.Commands.ON, r),
            (t + 0.60, Show.Commands.OFF, r)] # yapf:disable

  def ReStart(self):
    super(GrinchShow, self).ReStart()
    self._sliding = None

    on = Options.ondelay
    heartDelay = 1.5
    self.LoadTimings([
        #starting state
        (0, Show.Commands.ON, Show.Relays.OLAF_FAN),
        (0, Show.Commands.ON, Show.Relays.GRINCH_FAN),
        (0, Show.Commands.ON, Show.Relays.GRINCH_SLEIGH_FAN),
        (0, Show.Commands.OFF, Show.Relays.OLAF),
        (0, Show.Commands.OFF, Show.Relays.LASER_PROJ),
        (0, Show.Commands.OFF, Show.Relays.REINDEER),
        (0, Show.Commands.OFF, Show.Relays.SNOWMAN),
        (0, Show.Commands.OFF, Show.Relays.GRINCH),

        # grinch is turning things back on
        (0.01, Show.Commands.ON, Show.Relays.GRINCH_SLEIGH),

        # run the heart sequence
        (heartDelay, GrinchShow.GrinchCommands.START_HEART)
    ])

  def RestoreLights(self):
    on = 0
    self.LoadTimings([
        # now start to turn things on
        GrinchShow.FlashOn(on + 0, Show.Relays.REINDEER),
        GrinchShow.FlashOn(on + 1, Show.Relays.OLAF),
        GrinchShow.FlashOn(on + 2, Show.Relays.SNOWMAN),
        (on + 3, Show.Commands.ON, Show.Relays.LASER_PROJ),
        (on + 4.5, GrinchShow.GrinchCommands.PIXEL_SHOW),
        GrinchShow.FlashOff(on + 6, Show.Relays.GRINCH_SLEIGH),
        (on + 6, GrinchShow.GrinchCommands.HEART_OFF),
      ])

  # advance to the next pixel show and decide whether to do grinch show or not
  def PixelShow(self):
    print("New Pixel Show")
    self.LoadTimings([(0, Show.Commands.PIXELS_ON)])
    if (random.random() < Options.grinchprob):
      print ("Planning Grinch")
      self.LoadTimings([(Options.holdtime, GrinchShow.GrinchCommands.START_GRINCH)])
    else:
      print ("No Grinch")
      self.LoadTimings([(Options.holdtime, GrinchShow.GrinchCommands.PIXEL_SHOW)])
      

  # when grinch appears then sequence until all off
  def StartGrinch(self):
    print("GRINCH")
    off = Options.grinchoffdelay
    self.LoadTimings([
        GrinchShow.FlashOn(0, Show.Relays.GRINCH),
        (off, GrinchShow.GrinchCommands.BIKE_OFF),
        (off + 1.5, GrinchShow.GrinchCommands.START_SLIDE)
    ])

  def StartSlide(self):
    print("start slide")
    gc.collect()
    self._sliding = self._display.SlideLeft()
    self._finished = False

  def FinishSlide(self):
    print("finish slide")
    gc.collect()
    self._sliding = self._display.SlideLeft()
    self._finished = True

  def EndGrinch(self):
    print("end GRINCH")
    off = 1.5
    s = off + 5
    self.LoadTimings([
      GrinchShow.FlashOff(off, Show.Relays.REINDEER),
      GrinchShow.FlashOff(off + 1.5, Show.Relays.OLAF),
      GrinchShow.FlashOff(off + 3, Show.Relays.SNOWMAN),
      (off + 4, Show.Commands.OFF, Show.Relays.LASER_PROJ),
      # manual flash
      (s + 0, Show.Commands.OFF, Show.Relays.GRINCH),
      (s + 0.05, Show.Commands.ON, Show.Relays.GRINCH),
      (s + 0.15, Show.Commands.OFF, Show.Relays.GRINCH),
      (s + 0.25, Show.Commands.ON, Show.Relays.GRINCH),
      (s + 0.25, GrinchShow.GrinchCommands.FINISH_SLIDE),
      GrinchShow.FlashOff(s + 1.75, Show.Relays.GRINCH),
      (s + 4 + Options.darktime, Show.Commands.RESTART)
    ])

  def _animateNextFrame(self):
    self._heart.AnimateNextFrame()
    if (self._sliding is not None):
      if not next(self._sliding):
        self._sliding = None
        if (not self._finished):
          # schedule final scene after first slide finishes
          self.EndGrinch()
        else:
          # after final slideoff and disappear, stop sparkling
          self._sparkler = None
          print("done")


def main():
  GrinchShow.SetArgs(Options.parser)
  Heart.SetArgs(Options.parser)
  Options.ParseArgs()
  show = GrinchShow()
  show.Run()


if __name__ == '__main__':
  main()
