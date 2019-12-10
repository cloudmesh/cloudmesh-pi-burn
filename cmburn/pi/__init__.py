import os
import sys

if sys.version_info[0] < 3:
    raise Exception("You must be using Python 3")

try:
    columns, lines = os.get_terminal_size()
except:
    columns = 80
    lines = 24