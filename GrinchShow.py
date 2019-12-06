import enum
import argparse
import gc

from Show import Show

class GrinchShow(Show):
  def __init__(self, options):
    super(GrinchShow, self).__init__(options)
    self._sliding = None


  @staticmethod
  def SetArgs(parser):
    parser.add_argument('--ondelay', type=int, default=3, help="delay between grinch sleigh appear and lights on")
    parser.add_argument('--grinchoffdelay', type=int, default=2, help="delay between grinch sleigh appear and lights turning off")
    parser.add_argument('--startslide', type=int, default=35, help="start grinch slide at seconds")
    parser.add_argument('--darktime', type=int, default=6, help="time to remain dark after slide before reset")


  # commands used by Grinch animation
  class GrinchCommands(enum.Enum):
    START_GRINCH = 1 # grinch appears in his sleigh and steals the lights
    START_SLIDE = 2 # grinch begins pulling the lights (pixels) off the house
    FINISH_SLIDE = 3 # grinch is now finished (has coil of lights) so slide them off too

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
      else:
        raise NotImplementedError(e)
    else:
      super(GrinchShow, self).LoadTiming(e)

  def ReStart(self):
    super(GrinchShow, self).ReStart()
    self._sliding = None

    on = self._options.ondelay
    self.LoadTimings( [
      #starting state
      (0, Show.Commands.ON, Show.Relays.OLAF_FAN),
      (0, Show.Commands.ON, Show.Relays.GRINCH_FAN),
      (0, Show.Commands.ON, Show.Relays.GRINCH_SLEIGH_FAN),
      (0, Show.Commands.OFF, Show.Relays.OLAF),
      (0, Show.Commands.OFF, Show.Relays.LASER_PROJ),
      (0, Show.Commands.OFF, Show.Relays.REINDEER),
      (0, Show.Commands.OFF, Show.Relays.SNOWMAN),
      (0, Show.Commands.ON, Show.Relays.GRINCH_SLEIGH),
      (0, Show.Commands.OFF, Show.Relays.GRINCH),

      # now start to turn things on
      (on, Show.Commands.ON, Show.Relays.OLAF),
      (on+1, Show.Commands.ON, Show.Relays.REINDEER),
      (on+2, Show.Commands.ON, Show.Relays.SNOWMAN),
      (on+3, Show.Commands.ON, Show.Relays.LASER_PROJ),
      (on+5, Show.Commands.PIXELS_ON),

      (on+7, Show.Commands.OFF, Show.Relays.GRINCH_SLEIGH),
      (on+6+self._options.startslide, GrinchShow.GrinchCommands.START_GRINCH),
    ])

# when grinch appears then sequence until all off
  def StartGrinch(self):
    print "GRINCH"
    off = self._options.grinchoffdelay
    s = off + 6 + 1
    t = s + 1.5
    self.LoadTimings( [
      (0, Show.Commands.ON, Show.Relays.GRINCH_SLEIGH),
      (0.1, Show.Commands.OFF, Show.Relays.GRINCH_SLEIGH),
      (0.3, Show.Commands.ON, Show.Relays.GRINCH_SLEIGH),
      (0.6, Show.Commands.OFF, Show.Relays.GRINCH_SLEIGH),
      (1.0, Show.Commands.ON, Show.Relays.GRINCH_SLEIGH),

      (off, Show.Commands.OFF, Show.Relays.OLAF),
      (off+2, Show.Commands.OFF, Show.Relays.REINDEER),
      (off+4, Show.Commands.OFF, Show.Relays.SNOWMAN),
      (off+6, Show.Commands.OFF, Show.Relays.LASER_PROJ),

      (s+0, Show.Commands.OFF, Show.Relays.GRINCH_SLEIGH),
      (s+0.1, Show.Commands.ON, Show.Relays.GRINCH_SLEIGH),
      (s+.4, Show.Commands.OFF, Show.Relays.GRINCH_SLEIGH),
      (s+.8, Show.Commands.ON, Show.Relays.GRINCH_SLEIGH),
      (s+1.1, Show.Commands.OFF, Show.Relays.GRINCH_SLEIGH),

      (t+0, Show.Commands.ON, Show.Relays.GRINCH),
      (t+0.1, Show.Commands.OFF, Show.Relays.GRINCH),
      (t+0.3, Show.Commands.ON, Show.Relays.GRINCH),
      (t+0.4, Show.Commands.OFF, Show.Relays.GRINCH),
      (t+0.8, Show.Commands.ON, Show.Relays.GRINCH),
    
      (t+1.5, GrinchShow.GrinchCommands.START_SLIDE)
    ])


  def StartSlide(self):
    print "start slide"
    gc.collect()
    self._sliding = self._display.SlideLeft()
    self._finished = False

  def FinishSlide(self):
    print "finish slide"
    gc.collect()
    self._sliding = self._display.SlideLeft(True)
    self._finished = True
    
  def EndGrinch(self):
    s = self._options.grinchoffdelay
    self.LoadTimings( [
      (s+0, Show.Commands.OFF, Show.Relays.GRINCH),
      (s+0.3, Show.Commands.ON, Show.Relays.GRINCH),
      (s+1, Show.Commands.OFF, Show.Relays.GRINCH),
      (s+1, GrinchShow.GrinchCommands.FINISH_SLIDE),
      (s+1.4, Show.Commands.ON, Show.Relays.GRINCH),
      (s+1.9, Show.Commands.OFF, Show.Relays.GRINCH),
      (s+3+self._options.darktime, Show.Commands.RESTART)
    ])

    
  def _animateNextFrame(self):
    if (self._sliding is not None):
      if (not self._sliding.next()):
        self._sliding = None
        if (not self._finished):
          # schedule final scene after first slide finishes
          self.EndGrinch()
        else:
          # after final slideoff and disappear, stop sparkling
          self._sparkler = None


    
def main():
  parser = argparse.ArgumentParser()
  Show.setupArgs(parser)
  GrinchShow.SetArgs(parser)

  options = parser.parse_args()
  print "args are" , options
  show = GrinchShow(options)
  show.Run()


if __name__ == '__main__':
  main()
