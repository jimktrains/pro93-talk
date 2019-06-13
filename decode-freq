#!/usr/bin/env python3

import sys
import decoder


# remove the first which is the program name
sys.argv.pop(0)

for i in sys.argv:
    bs = bytes.fromhex(i)
    mem=decoder.freq_memory.decode(bs)
    print(bs.hex() + " => " + str(mem))
