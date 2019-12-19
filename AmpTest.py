# turn on 50 pixels (typical one physical strand) for amperage tests

from ola.ClientWrapper import ClientWrapper
from Relays import Relays
from Show import Show
from Options import Options
import array
import os
import argparse
import time

def DmxSent(state):
  if not state.Succeeded():
    print ("Error: ", state.message)
    raise


Options.ParseArgs()

wrapper = ClientWrapper()
relays = Relays(wrapper)

# turn on 12v (on NC so sense is reversed)
# (conincidentally turns off everything else, too)
# (should already be off)
print "12v on"
relays.off(Show.Relays.POWER)
relays.SendDmx()

time.sleep(8)

length = 50
pixels = array.array('B', [int(255*1)] * length*3)

wrapper.Client().SendDmx(2, pixels, DmxSent)
print "white sent 50 pixels to univ 2"
time.sleep(2)
wrapper.Run()

