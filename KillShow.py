# kill running shows (really just other python scripts)

from ola.ClientWrapper import ClientWrapper
from Relays import Relays
from Show import Show
from Options import Options

import os
import time

Options.ParseArgs()

# kill any currently running shows
os.system('killall -r --older-than 5s python?')

# turn off 12v (on NC so sense is reversed)
# (conincidentally turns off everything else, too)
# turn power supply on 
os.system('gpio -g write 2 1')
