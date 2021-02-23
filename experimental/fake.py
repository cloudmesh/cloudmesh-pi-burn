#!/usr/bin/env python

import sys
import time

for i in range(0,100):

    time.sleep(0.01)

    time.sleep(1)
    print(i)
    sys.stdout.flush()
