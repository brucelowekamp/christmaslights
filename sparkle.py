import array
from ola.ClientWrapper import ClientWrapper
import math
import time
import random
import colorsys

USE_RELAYS = False #disable AC relay/GPIO (universe 10)

SLIDE_START_MS = 100*1000
RESET_DISPLAY_MS = 120*1000

wrapper = None
TICK_INTERVAL_MS = 50  # in ms
TICK_INTERVAL_S = TICK_INTERVAL_MS/1000.0
TICK_PER_SEC = 1000//TICK_INTERVAL_MS

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
    self._slide_remaining = max(self._strand_length)
    self._map = [] # tuples for all pixels of (strand_n, pixel_n )
    for i in range(self._num_strands):
      for j in range (self._strand_length[i]):
        self._map.append( (i , j ) )

  @property
  def length(self):
    return len(self._map)
      
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

  # iterates across the map.  map tuples can be treated transparently and passed to ColorSet
  def __iter__(self):
    return iter(self._map)
  
  #return [R, G, B] of pixel from global index
  def ColorGet(self, pixel):
    (s, p) = pixel
    return self._pixels[s][p*3+0], self._pixels[s][p*3+1],self._pixels[s][p*3+2]

  #return [R, G, B] of pixel (0-based) on strand
  def ColorGetStrand(self, strand, pixel):
    assert strand < self._num_strands
    assert pixel < self._strand_length[strand]
    return self._pixels[strand][pixel*3+0], self._pixels[strand][pixel*3+1],self._pixels[strand][pixel*3+2]

  # set pixel from global index to color ([ R, G, B ])
  def ColorSet(self, pixel, red, green, blue):
    (s, p) = pixel
    self._pixels[s][p*3+0] = red
    self._pixels[s][p*3+1] = green
    self._pixels[s][p*3+2] = blue

  # set pixel on strand to color ([ R, G, B ])
  def ColorSetStrand(self, strand, pixel, red, green, blue):
    assert strand < self._num_strands
    assert pixel < self._strand_length[strand]
    self._pixels[strand][pixel*3+0] = red
    self._pixels[strand][pixel*3+1] = green
    self._pixels[strand][pixel*3+2] = blue

  # slide all strings left and return true/false if more to slide
  def SlideLeft(self):
    if (self._slide_remaining > 0):
      for i in range(self._num_strands):
        self._pixels[i].pop(0)
        self._pixels[i].pop(0)
        self._pixels[i].pop(0)
        self._pixels[i].extend([0,0,0])
      self._slide_remaining -= 1
    return self._slide_remaining > 0
  
  def SendDmx(self):
    for i in range(self._num_strands):
      wrapper.Client().SendDmx(self._strand_universe[i], self._pixels[i], DmxSent)


class Relays(object):
  def __init__(self):
    self._dmx = array.array('B', [0, 0, 0])
    self._send = False
    self._universe = 10

  @property
  def send(self):
    return self._send

  def on(self, channel):
    self._dmx[channel] = 255
    self._send = True

  def off(self, channel):
    self._dmx[channel] = 0
    self._send = True

  def SendDmx(self):
    if(USE_RELAYS): wrapper.Client().SendDmx(self._universe, self._dmx, DmxSent)
    self._send = False

# compute frame here

def RedGreen(display):
  print ("RedGreen pattern")
  i = 0
  for p in display:
    red = (i//5)%2 == 0
    display.ColorSet(p, 255 if red else 0, 0 if red else 255, 0)
    i+=1

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
        display.ColorSetStrand(s, base + delta, red, green, 0) 

def White(display):
  print ("White")
  for p in display:
    display.ColorSet(p, 255, 255, 255)

def Rainbow(display):
  print ("Rainbow")
  for s in range(display.num_strands):
    l = display.StrandLength(s)
    for p in range(l):
      (r, g, b) = colorsys.hsv_to_rgb((p*1.0)/l, 1, 1)
      display.ColorSetStrand(s, p, int(r*255), int(g*255), int(b*255))
    
LightPatterns = [RedGreen, RGFade, White, Rainbow]

GPIO_FANS = 0
GPIO_OLAF = 1
GPIO_GRINCH = 2

#pass via lambda?
loop_count = 0
relays = Relays()
display = None
sliding = False
draw = False
target_time = time.time()
def StartSlide():
  global sliding
  
  print "start slide"
  sliding = True

def NewDisplay():
  global draw
  global loop_count
  global sliding
  global display
  global relays
  
  loop_count = 0
  sliding = False
  display = Display()
  random.choice(LightPatterns)(display)
  draw = True
  wrapper.AddEvent(0, lambda: relays.on(GPIO_FANS))
  wrapper.AddEvent(0, lambda: relays.on(GPIO_OLAF))
  wrapper.AddEvent(0, lambda: relays.off(GPIO_GRINCH))
  wrapper.AddEvent(SLIDE_START_MS-3000, lambda: relays.off(GPIO_OLAF))
  wrapper.AddEvent(SLIDE_START_MS-3000, lambda: relays.on(GPIO_GRINCH))
  wrapper.AddEvent(SLIDE_START_MS, StartSlide)
  wrapper.AddEvent(0, lambda: relays.off(GPIO_GRINCH))
  wrapper.AddEvent(RESET_DISPLAY_MS, NewDisplay)

# send frame precomputed last call, then compute frame and schedule next call
def SendFrame():
  global display
  global loop_count
  global sliding
  global draw
  global target_time

  # send if we should, first thing to time as precisely as we can
  if (draw): display.SendDmx()
  if (relays.send): relays.SendDmx()
  if (loop_count % (TICK_PER_SEC*10) == 0): print "loop: ", loop_count // TICK_PER_SEC

  draw = False

  if (sliding):
    sliding = display.SlideLeft()
    draw = True

  # schedule a function call for remaining time
  # we do this last with the right sleep time in case the frame computation takes a long time.
  next_target = target_time + TICK_INTERVAL_S
  delta_time = next_target - time.time()
  if (delta_time < 0): #hiccup, fell behind, one extra call
    target_time = time.time()+0.001 # make an extra call faking one ms progress, drop the rest
    print "hiccup!"
    SendFrame()
  else:
    target_time = next_target
    wrapper.AddEvent(int(delta_time*1000), SendFrame)

  loop_count += 1


NewDisplay()
SendFrame()
wrapper.Run()
