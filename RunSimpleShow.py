# run overall system without grinch
# single paramater --showname is name of show in shows directory

from ola.ClientWrapper import ClientWrapper
from Relays import Relays
from Show import Show
from Options import Options
import os
import sys
import time

pythonexec = sys.executable

def ShownameArg(parser):
  parser.add_argument('--showname',
                      type=str,
                      default=None,
                      help="file in shows directory to get show params from")


Options.ParseArgs(additional=ShownameArg)
assert(Options.showname is not None)

# kill any currently running shows
os.system('killall -r --older-than 5s python?')

# turn power supply on 
os.system('gpio -g write 2 0')

time.sleep(10)

# restart olad
os.system('sudo /etc/init.d/olad restart')


#wrapper = ClientWrapper()
#relays = Relays(wrapper)



# turn off 12v (on NC so sense is reversed)
# (conincidentally turns off everything else, too)
# (should already be off)
#relays.on(Show.Relays.POWER)
#relays.SendDmx()

#time.sleep(5)

#relays.off(Show.Relays.POWER)
#relays.SendDmx()

time.sleep(8)

# run program in loop
while True:
  os.system(pythonexec+' SimpleShow.py @shows/'+Options.showname)
  print("SHOW LOOPING!!!!!")
  time.sleep(1)

  # run this reset every time b/c if the code exits there is a reason
  os.system('sudo /etc/init.d/olad restart')

  time.sleep(5)
