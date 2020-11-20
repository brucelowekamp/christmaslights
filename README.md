# Grinch Steals the Christmas Lights

This program implements a Christmas light show of pixels strung across
a house plus various other features (inflatables and string lights)
on relay-switched AC outlets. The main show features a grinch
(inflatable) who appears at the side of the house and then pulls the
lights off the house (the lights slide across the house onto a coil in
front of the Grinch).

This uses the [Open Lighting Alliance (OLA)
API](https://github.com/OpenLightingProject/ola) client/server to send
DMX for the pixels and relays.  It was developed on a Raspberry Pi
using E1.31 (DMX over UDP) to control the pixels and RPi GPIO for the
relays, but in principle it would just take an olad setup change to
map the relay universe to a E1.31-based relay module instead of an
RPi. 

Language is python 3.  Needs "pip install enum34"


There are two versions of the show, SimpleShow, which only displays
various color patterns on the lights, and GrinchShow that lights up
the grinch sleigh on the roof and has the grinch pull the lights off
the house.  The grinch show looks better when it's dark enough you
don't see the sleigh on the roof until it lights up.

The relay configuration is currently hard-coded into the program
itself, as are the event sequences.

As of March the SimpleShow was modified to be used as uplifting
lighting for Easter and isolation.  Adds Easter colors plus US,
Italian, Spanish, and English flags, plus Blue. Parameterization was
added to take strand definition and patterns in use from commandline.

The program relies on OLA python library's ClientWrapper to send the
DMX data and for the event loop.  The main animation loop runs at 20Hz
and various animations are based on ticks at that rate.  Show story
(grinch appearing, turning relays on/off for reindeer, snowman, etc)
are done with raw events (clock-based) rather than in the animation
loop, so each segment of the show is loaded in a batch into the OLA
event loop.

The show restricts the pixels to 50% of maximum brightness as full
brightness is too bright and running at lower power allows longer runs
without running extra power injection lines into the display.  However
for "Twinkle" effects the individual pixels can go to 100%.  The
implementation would assert if an overall pixel strand is set to more
than 50% average power (normal usage is 40%).

Also, for safety of the rooftop sleigh inflatable, there is a
--nosleigh option that should be used to not inflate the sleigh when
winds are high.

## Code Overview

Show.py: core Show base class.

- Relays: Show element (inflatable, lights, etc) DMX channel mapping
for relays
- Commands: event action (making this an enum rather than a
function allows some processing and renaming to be done more
easily)
- SendFrame: main event loop
  - first sends DMX from previous computed next frame
  - next calls all next frame animation and runs sparkler
  - short circuit if show lags (already up to next draw cycle) otherwise schedules next call
- Every show needs to finish by calling ReStart that resets
everything and begins again


SimpleShow: all this does is turn on the non-grinch elements and
rotate the light pattern every minute.   Implements main() for that show.

GrinchShow: Sequences for grinch appearing etc.  Per-frame animation
for sliding the lights off.  Implements main() for that show

Run{Grinch|Simple}Show: main runner called via cron.  kills off any
other show (i.e. all python running), resets olad, GPIO, and the Pixel
Controller, then runs the show.  If it exits, restarts olad and
restarts the show.  At present there is no feedback from the
controller and if it crashes there is no way to know (and it's only
reset at the beginning of the show)

KillShow: kills the show and turns off all the relays and pixel controller

PixelDisplay: class for representing the pixel part of the display:

- PixelDisplay: main class, holds a set of Strand
- Strand: straight stretch of pixels, can be multiple strands
- implements sending dmx, sliding (as generator) and get/set
either via display or strand


PixelPatterns: various methods for interesting color patterns for the
pixels

Sparkler: adds some flare

- twinkle: lights randomly flash quickly to white and back
- flow: lights slowly change colors, sometimes back or not

Relays: controls the relays (via DMX mapped to GPIO on RPi)

### Utilities
Options: global for passing command line args

Ranges: utility for parsing 1,3-4,6 strings for pixels to be lit

wl\_to\_rgb: sweep wavelength along spectrum for rainbow display.
Though this still wasn't right (in both RGB land and real spectrum
some colors take less range than others) so there's another function
in pattern to spread things out by eye

rpi-setup: various files for debian and olad setup


AmpTest: utility to turn on lights full white for current measurement


## general notes
to turn pixels on without relays module: gpio -g write 2 0

then run with --norelays option to test pixels only

to turn pixels off without relays: gpio -g write 2 1



# TODO
- move flickering on or off should be moved to the animation loop from the
show events.
- move to numpy and use slices rather than copying
- align on colors as tuples rather than red, green, blue
