from Options import Options
from Show import Show


class SimpleShow(Show):

  def __init__(self):
    super(SimpleShow, self).__init__()

  @staticmethod
  def SetArgs(parser):
    parser.add_argument('--holdtime', type=int, default=60, help="time before changing pattern")
    parser.add_argument('--grincheson', action="store_true", help="turn on even grinch and sleigh")

  def ReStart(self):
    super(SimpleShow, self).ReStart()
    grinches = Show.Commands.OFF if not Options.grincheson else Show.Commands.ON
    self.LoadTimings([
        #starting state
        (0, Show.Commands.ON, Show.Relays.OLAF_FAN),
        (0, grinches, Show.Relays.GRINCH_FAN),
        (0, grinches, Show.Relays.GRINCH_SLEIGH_FAN),
        (0, Show.Commands.ON, Show.Relays.OLAF),
        (0, Show.Commands.ON, Show.Relays.LASER_PROJ),
        (0, Show.Commands.ON, Show.Relays.REINDEER),
        (0, Show.Commands.ON, Show.Relays.SNOWMAN),
        (0, grinches, Show.Relays.GRINCH_SLEIGH),
        (0, grinches, Show.Relays.GRINCH),

        # pixels are on
        (0, Show.Commands.PIXELS_ON),
        (Options.holdtime, Show.Commands.RESTART)
    ])


def main():
  SimpleShow.SetArgs(Options.parser)
  Options.ParseArgs()
  if Options.inside:
    Options.relays = False
  show = SimpleShow()
  show.Run()


if __name__ == '__main__':
  main()
