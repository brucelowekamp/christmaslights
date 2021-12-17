import datetime
import os
from suntime import Sun

latitude = 37.2
longitude = -76.7

sunset = Sun(latitude, longitude).get_local_sunset_time()

simpletime = sunset - datetime.timedelta(minutes=15)
grinchtime = sunset + datetime.timedelta(minutes=30)

print (f"sunset is {sunset}")
print (f"simple {simpletime.strftime('%H:%M')} grinch {grinchtime.strftime('%H:%M')}")


os.system(f"at {simpletime.strftime('%H:%M')} -f ScheduleSimpleCommand.sh")
os.system(f"at {grinchtime.strftime('%H:%M')} -f ScheduleGrinchCommand.sh")
