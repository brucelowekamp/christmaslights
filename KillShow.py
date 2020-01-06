# kill running shows (really just other python scripts)

from ola.ClientWrapper import ClientWrapper
from Relays import Relays
from Show import Show
from Options import Options

import os
import time

Options.ParseArgs()

# kill any currently running shows
os.system('killall --older-than 1m python')

# restart olad
os.system('sudo /etc/init.d/olad restart')

time.sleep(5)

wrapper = ClientWrapper()
relays = Relays(wrapper)

# turn off 12v (on NC so sense is reversed)
# (conincidentally turns off everything else, too)
relays.on(Show.Relays.POWER)
relays.SendDmx()

time.sleep(5)
