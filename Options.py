import argparse

import Show
import PixelDisplay
import Relays
import PixelPatterns
import Sparkler

opts = None

def SetGlobalArgs(parser):
  global opts

  Show.Show.SetArgs(parser)
  PixelDisplay.PixelDisplay.SetArgs(parser)
  Relays.Relays.SetArgs(parser)
  PixelPatterns.PixelPatterns.SetArgs(parser)
  Sparkler.Sparkler.SetArgs(parser)
  opts = parser.parse_args()
  print "args are" , opts