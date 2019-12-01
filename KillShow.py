# kill running shows (really just other python scripts)

from ola.ClientWrapper import ClientWrapper
from Relays import Relays
from GrinchShow import *

import os
import argparse
import time

parser = argparse.ArgumentParser()
Relays.SetArgs(parser)
options = parser.parse_args()

# kill any currently running shows
os.system('killall --older-than 1m python')

# restart olad
os.system('sudo /etc/init.d/olad restart')

time.sleep(5)

wrapper = ClientWrapper()
relays = Relays(wrapper, options)

# turn off 12v (on NC so sense is reversed)
# (conincidentally turns off everything else, too)
relays.on(Relay.POWER)
relays.SendDmx()

time.sleep(5)




