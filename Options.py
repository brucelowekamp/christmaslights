import argparse

class _Options(object):
  def __init__(self):
    self._parser = argparse.ArgumentParser()
    self._options = None

  def __getattr__(self, attr):
    return getattr(self._options, attr)

  @property
  def parser(self):
    return self._parser

  def ParseArgs(self):
    import Show
    import PixelDisplay
    import Relays
    import PixelPatterns
    import Sparkler

    Show.Show.SetArgs(self._parser)
    PixelDisplay.PixelDisplay.SetArgs(self._parser)
    Relays.Relays.SetArgs(self._parser)
    PixelPatterns.PixelPatterns.SetArgs(self._parser)
    Sparkler.Sparkler.SetArgs(self._parser)

    self._options = self._parser.parse_args()

    print ("args are" , self._options)

Options = _Options()
