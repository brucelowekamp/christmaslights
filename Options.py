import argparse
import logging

class _Options(object):

  # also read options from @filename max one per line, ignore comment lines
  class MyArgumentParser(argparse.ArgumentParser):
    def __init__(self):
      super(_Options.MyArgumentParser, self).__init__(fromfile_prefix_chars='@')
      
    def convert_arg_line_to_args(self, arg_line):
      if arg_line.startswith('#'):
        return []
      else:
        return arg_line.split(' ', 1)
      
  def __init__(self):
    self._parser = _Options.MyArgumentParser()
    self._options = None

  def __getattr__(self, attr):
    return getattr(self._options, attr)

  @property
  def parser(self):
    return self._parser

  def ParseArgs(self, additional=None):
    import Show
    import PixelDisplay
    import Relays
    import PixelPatterns
    import Sparkler
    import Bicycle

    Show.Show.SetArgs(self._parser)
    PixelDisplay.PixelDisplay.SetArgs(self._parser)
    Relays.Relays.SetArgs(self._parser)
    PixelPatterns.PixelPatterns.SetArgs(self._parser)
    Sparkler.Sparkler.SetArgs(self._parser)
    Bicycle.Bicycle.SetArgs(self._parser)
    if additional is not None:
      additional(self._parser)
    self._parser.add_argument('--loglevel', default="WARNING")
    self._options = self._parser.parse_args()

    print("args are", self._options)

    numeric_level = getattr(logging, self.loglevel.upper(), None)
    if not isinstance(numeric_level, int):
      raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(format='%(levelname)s:%(filename)s:%(message)s', level=numeric_level)


Options = _Options()
