import array
from ola.ClientWrapper import ClientWrapper
import math
import time

wrapper = None

def DmxSent(state):
  if not state.Succeeded():
    print ("Error: "+state)
    wrapper.Stop()


wrapper = ClientWrapper()

# compute frame here
data = array.array('B')

for i in range(100):
  light = array.array('B', [0, 0, 0])
  light[i%2] = 255
  data.extend(light)

wrapper.Client().SendDmx(1, data, DmxSent)

time.sleep (2)

data = array.array('B')
  
  
for i in range(300):
  data.append(0)

LENGTH=100
NUMSETS=5
SETSIZE = int(LENGTH/NUMSETS)

for set in range(NUMSETS):
  base = set * SETSIZE*3
  color = set % 3
  for pixel in range(SETSIZE):
    #data[base+pixel*3+color] = int((pixel+1)/SETSIZE*255)
    print (int(math.exp((pixel+1)/SETSIZE*6-6)*255))
    data[base+pixel*3+color] = int(math.exp((pixel+1)/SETSIZE*6-6)*255)

wrapper.Client().SendDmx(1, data, DmxSent)


#wrapper.Run()
