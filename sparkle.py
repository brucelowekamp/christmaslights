import array
from ola.ClientWrapper import ClientWrapper
import math
import time
import random

wrapper = None
TICK_INTERVAL = 100  # in ms
TICK_PER_SEC = 1000//TICK_INTERVAL

wrapper = ClientWrapper()

def DmxSent(state):
  if not state.Succeeded():
    print ("Error: ", state.message)
    wrapper.Stop()

class Display(object):
  
  def __init__(self):
    self._num_strands = 2
    self._strand_length = [100, 50]
    self._strand_universe = [1, 2]
    self._pixels= [ None ] * self._num_strands
    for i in range(self._num_strands):
      self._pixels[i] = array.array('B', [0] * (3 * self._strand_length[i]))
      
  @property
  def num_strands(self):
    return self._num_strands

  @property
  def max_strand_length(self):
    return max(self._strand_length)
  
  # return length of strand
  def StrandLength(self, strand):
    assert strand < self._num_strands
    return self._strand_length[strand]

  #return [R, G, B] of pixel (0-based) on strand
  def ColorGet(self, strand, pixel):
    assert strand < self._num_strands
    assert pixel < self._strand_length[strand]
    return [ self._pixels[strand][pixel*3+0],
             self._pixels[strand][pixel*3+1],
             self._pixels[strand][pixel*3+2] ]

  # set pixel on strand to color ([ R, G, B ])
  def ColorSet(self, strand, pixel, red, green, blue):
    assert strand < self._num_strands
    assert pixel < self._strand_length[strand]
    self._pixels[strand][pixel*3+0] = red
    self._pixels[strand][pixel*3+1] = green
    self._pixels[strand][pixel*3+2] = blue

  def SlideLeft(self):
    for i in range(self._num_strands):
      self._pixels[i].pop(0)
      self._pixels[i].pop(0)
      self._pixels[i].pop(0)
      self._pixels[i].extend([0,0,0])
      
  def SendDmx(self):
    for i in range(self._num_strands):
      wrapper.Client().SendDmx(self._strand_universe[i], self._pixels[i], DmxSent)

    

# compute frame here

def RedGreen(display):
  print ("RedGreen pattern")
  for s in range(display.num_strands):
    for i in range(display.StrandLength(s)):
      red = (i//5)%2 == 0
      display.ColorSet(s, i, 255 if red else 0, 0 if red else 255, 0)

def RGFade(display):
  print ("RGFade pattern")

  NUMSETS=10
  for s in range(display.num_strands):

    SETSIZE = display.StrandLength(s)//NUMSETS

    for set in range(NUMSETS):
      base = set * SETSIZE
      color = set % 2
    
      for pixel in range(SETSIZE):
        #print (int(math.exp((pixel+1.0)/SETSIZE*6-6)*255))
        faded = int(math.exp((pixel+1.0)/SETSIZE*6-6)*255)
        red = faded if set % 2 == 0 else 0
        green = 0 if set % 2 == 0 else faded
        delta = pixel if set % 2 == 0 else SETSIZE - pixel - 1
        display.ColorSet(s, base + delta, red, green, 0) 

def White(display):
  print ("White")
  for s in range(display.num_strands):
    for i in range(display.StrandLength(s)):
      display.ColorSet(s, i, 255, 255, 255)

LightPatterns = [RedGreen, RGFade, White]

loop_count = 0
slide_count = 0
display = None


def SendFrame():
  global display
  global loop_count
  global sliding
  global slide_count
  global TICK_PER_SEC
  
  # schdule a function call in 100ms
  # we do this first in case the frame computation takes a long time.
  wrapper.AddEvent(TICK_INTERVAL, SendFrame)
  if (loop_count % TICK_PER_SEC == 0): print ("loop: ", loop_count)
  draw = False
  if (loop_count == 0):
    display = Display()
    random.choice(LightPatterns)(display)
    #wrapper.Client().SendDmx(10, array.array('B', [255, 0, 0]), DmxSent)
    draw=True
  elif (loop_count == 100*TICK_PER_SEC):
    print ("start slide")
    #wrapper.Client().SendDmx(10, array.array('B', [0, 255, 255]), DmxSent)
    slide_count = display.max_strand_length
  elif (loop_count == 120*TICK_PER_SEC):
    loop_count = -1

  if (slide_count > 0):
    display.SlideLeft()
    draw = True
    slide_count-=1
    
  loop_count += 1
  # send
  if (draw): display.SendDmx()

wrapper.AddEvent(TICK_INTERVAL, SendFrame)
wrapper.Run()
