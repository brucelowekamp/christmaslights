import enum

class Relay(enum.IntEnum):
  # first 8 slots are SSR max 2A for lights
  OLAF = 0
  LASER_PROJ = 1
  REINDEER = 2
  SNOWMAN = 3
  GRINCH_SLEIGH = 4
  GRINCH = 5

  # next 4 are leaf relay max 10A for fans
  OLAF_FAN = 8
  GRINCH_FANS= 9

  # last is local relay for 12V PS (for pixels)
  POWER = 12

class Commands(enum.Enum):
  ON = 0
  OFF = 1
  START_GRINCH = 2
  PIXELS_ON = 3
  FINISH_SLIDE = 4
  RESTART = 5
  START_SLIDE = 6



# initial start, do setup and then have grinch turn lights back on
def GrinchShowStart(options):
  on = options.ondelay
  return [
    #starting state
    (0, Commands.ON, Relay.OLAF_FAN),
    (0, Commands.ON, Relay.GRINCH_FANS),
    (0, Commands.OFF, Relay.OLAF),
    (0, Commands.OFF, Relay.LASER_PROJ),
    (0, Commands.OFF, Relay.REINDEER),
    (0, Commands.OFF, Relay.SNOWMAN),
    (0, Commands.ON, Relay.GRINCH_SLEIGH),
    (0, Commands.OFF, Relay.GRINCH),

    # now start to turn things on
    (on, Commands.ON, Relay.OLAF),
    (on+1, Commands.ON, Relay.LASER_PROJ),
    (on+2, Commands.ON, Relay.REINDEER),
    (on+3, Commands.ON, Relay.SNOWMAN),
    (on+4, Commands.PIXELS_ON),

    (on+6, Commands.OFF, Relay.GRINCH_SLEIGH),
    (on+6+options.startslide, Commands.START_GRINCH),
  ]

# when grinch appears then sequence until all off
def GrinchShowAppear(options):
  off = options.grinchoffdelay
  s = off + 6 + options.grinchoffdelay
  t = s + 2 + options.grinchoffdelay
  return [
    (0, Commands.ON, Relay.GRINCH_SLEIGH),
    (0.2, Commands.OFF, Relay.GRINCH_SLEIGH),
    (0.7, Commands.ON, Relay.GRINCH_SLEIGH),
    (1.1, Commands.OFF, Relay.GRINCH_SLEIGH),
    (1.5, Commands.ON, Relay.GRINCH_SLEIGH),

    (off, Commands.OFF, Relay.OLAF),
    (off+2, Commands.OFF, Relay.LASER_PROJ),
    (off+4, Commands.OFF, Relay.REINDEER),
    (off+6, Commands.OFF, Relay.SNOWMAN),

    (s+0, Commands.OFF, Relay.GRINCH_SLEIGH),
    (s+0.3, Commands.ON, Relay.GRINCH_SLEIGH),
    (s+1, Commands.OFF, Relay.GRINCH_SLEIGH),
    (s+1.3, Commands.ON, Relay.GRINCH_SLEIGH),
    (s+1.9, Commands.OFF, Relay.GRINCH_SLEIGH),

    (t+0, Commands.ON, Relay.GRINCH),
    (t+0.2, Commands.OFF, Relay.GRINCH),
    (t+0.7, Commands.ON, Relay.GRINCH),
    (t+1.1, Commands.OFF, Relay.GRINCH),
    (t+1.5, Commands.ON, Relay.GRINCH),
    
    (t+2.5, Commands.START_SLIDE)
  ]


def GrinchFinished(options):
  s = options.grinchoffdelay
  return [
    (s+0, Commands.OFF, Relay.GRINCH),
    (s+0.3, Commands.ON, Relay.GRINCH),
    (s+1, Commands.OFF, Relay.GRINCH),
    (s+1, Commands.FINISH_SLIDE),
    (s+1.3, Commands.ON, Relay.GRINCH),
    (s+1.9, Commands.OFF, Relay.GRINCH),
    (s+2+options.darktime, Commands.RESTART)
  ]

    
