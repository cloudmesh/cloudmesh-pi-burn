import os
import sys
from cmburn.pi.hardware import Hardware

if not Hardware.is_pi():
    print("ERROR: You must ron this on a Raspberry Pi. "
          "Dangerous things can happen if not!")
    sys.exit()
if sys.version_info[0] < 3:
    print("ERROR: You must be using Python 3")
    sys.exit()
if 'pi' not in sys.prefix:
    print("ERROR: You must be using a virtual env that is in the user pi")
    sys.exit()

# noinspection PyBroadException
try:
    columns, lines = os.get_terminal_size()
except:
    columns = 80
    lines = 24
