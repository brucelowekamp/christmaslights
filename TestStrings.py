# simple test of red, green, blue sequence

from ola.ClientWrapper import ClientWrapper
from PixelDisplay import PixelDisplay
from Relays import Relays
from Options import Options
import time

strandlist = f"PixelDisplay.Strand(wrapper, 1, PixelDisplay.StrandMap(ranges=\"0-200\"), 0)"
wrapper = ClientWrapper()
display = PixelDisplay(wrapper, strandlist=[strandlist])

while True:
    for p in display:
        display.ColorSet(p, 255, 0, 0)
    display.SendDmx()
    time.sleep(1)
    for p in display:
        display.ColorSet(p, 0, 255, 0)
    display.SendDmx()
    time.sleep(1)
    for p in display:
        display.ColorSet(p, 0, 0, 255)
    display.SendDmx()
    time.sleep(1)
