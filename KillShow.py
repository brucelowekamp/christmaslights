# kill running shows (really just other python scripts)

import os

# kill any currently running shows
os.system('killall -r --older-than 5s python?')

# turn off 12v (on NC so sense is reversed)
os.system('gpio -g write 2 1')

# turn off all other relays
for relay in range(11,23):
    os.system(f"gpio -g write {relay} 0")
