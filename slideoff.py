import array
from ola.ClientWrapper import ClientWrapper
import math
import time

wrapper = None
TICK_INTERVAL = 100  # in ms
TICK_PER_SEC = 1000/TICK_INTERVAL

LENGTH = 100
def DmxSent(state):
  if not state.Succeeded():
    print ("Error: "+state)
    wrapper.Stop()


wrapper = ClientWrapper()

# compute frame here

def RedGreen():
  print ("RedGreen pattern")
  data = array.array('B')
  for i in range(100):
    light = array.array('B', [0, 0, 0])
    light[(i/5)%2] = 255
    data.extend(light)
  return data

def RGFade():
  global LENGTH
  print ("RGFade pattern")
  data = array.array('B')
  for i in range(300):
    data.append(0)

  NUMSETS=10
  SETSIZE = int(LENGTH/NUMSETS)

  for set in range(NUMSETS):
    base = set * SETSIZE*3
    color = set % 2
    for pixel in range(SETSIZE):
      #print (int(math.exp((pixel+1.0)/SETSIZE*6-6)*255))
      data[base+pixel*3+color] = int(math.exp((pixel+1.0)/SETSIZE*6-6)*255)
  return data


def SlideLeft():
  global pixels
  # compute frame here
  pixels.pop(0)
  pixels.pop(0)
  pixels.pop(0)
  pixels.extend([0,0,0])

loop_count = 0
sliding = False
slide_count = 0
pattern = 0

def SendDMXFrame():
  global loop_count
  global sliding
  global slide_count
  global pixels
  global pattern
  global TICK_PER_SEC
  global LENGTH
  
  # schdule a function call in 100ms
  # we do this first in case the frame computation takes a long time.
  wrapper.AddEvent(TICK_INTERVAL, SendDMXFrame)
  if (loop_count % TICK_PER_SEC == 0): print ("loop: ", loop_count)
  draw = False
  if (loop_count == 120*TICK_PER_SEC):
    draw=True
    if (pattern == 0):
      pixels = RedGreen()
    else:
      pixels = RGFade()
      pattern = -1
    pattern += 1
    loop_count = 0

  if (loop_count == 100*TICK_PER_SEC):
    print ("start slide")
    sliding = True
    slide_count = 0

  if (sliding):
    SlideLeft()
    draw = True
    slide_count+=1

  if (slide_count == LENGTH): # ADD CONSTANT
    sliding = False;
    
  loop_count += 1
  # send
  if (draw): wrapper.Client().SendDmx(1, pixels, DmxSent)

pixels = RGFade()
wrapper.Client().SendDmx(1, pixels, DmxSent)

wrapper.AddEvent(TICK_INTERVAL, SendDMXFrame)
wrapper.Run()
