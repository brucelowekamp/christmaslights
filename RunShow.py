# run overall system

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


wrapper = ClientWrapper()
relays = Relays(wrapper, options)

# turn off 12v (on NC so sense is reversed)
# (conincidentally turns off everything else, too)
# (should already be off)
relays.on(Relay.POWER)
relays.SendDmx()

time.sleep(2)

# restart olad
os.system('sudo /etc/init.d/olad restart')

time.sleep(5)

wrapper = ClientWrapper()
relays = Relays(wrapper, options)

relays.off(Relay.POWER)
relays.SendDmx()

time.sleep(5)

# run program in loop
while True:
  os.system('python Show.py')
  print "SHOW LOOPING!!!!!"
  time.sleep(1)

  # run this reset every time b/c if the code exits there is a reason
  os.system('sudo /etc/init.d/olad restart')

  time.sleep(5)




