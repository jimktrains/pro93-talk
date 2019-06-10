#!/usr/bin/env python3

import struct

banks = 10
channels_per_bank = 30
channels = banks * channels_per_bank

sectionA = []
modes = []
labels = []

lockout = []
atten = []
delay = []
no_text_tag = []
freqs = []
unused = []


mode_map = {
    0:"AM",
    1:"FM",
    # Need to confirm
    2: "MO",
    3:"ED",
}

def extract_bits(b, first, last):
    """
###################################################################
#
# Extract a bit field from an 8-bit byte.
#
# Inputs:
#  byte  -an 8 bit byte
#  first  -first bit number
#  last  -last bit number (inclusive)
#
# Returns:
#  Integer value 0 - 255
#
# Notes:
#  Bits are numbered from left to right, i.e.,
#  01234567 with bit 0 being most significant
#
#  first <= last
###################################################################
"""
    # last + 1 because it's an inclusive it range and the `range` function
    # is exclusive
    #
    # 7-i because we're numbering the bits from mostsig to leastsig
    mask = sum([pow(2,7-i) for i in range(first, last+1)])

    # 7 - last because we're numbering from mostisg to leastsig and
    # we need to shift the result down into the least sig bits.
    return (b & mask) >> (7 - last)


fn = 'pro93-dump-2019-06-10T13:09:35.841920.bin'
with open(fn, 'rb') as f:

    for i in range(channels):
        bs = f.read(4)
        sectionA.append(bs)
        modes.append(extract_bits(bs[3], 6, 7))
        atten.append(extract_bits(bs[3], 5, 5))
        delay.append(extract_bits(bs[3], 4, 4))
        lockout.append(extract_bits(bs[3], 3, 3))

        # 3 bytes of a 4 byte Little Endian Integer are the first 3 bytes
        ef = bytearray(bs[0:3])
        ef.append(0)
        ef = struct.unpack("<L", ef)
        
        # Frequencies are stored in 250Hz increments
        freq = ef[0] * 250
        freqs.append(freq)

        # Bytes 090909 for the frequency represent an unused frequency.
        # 148.034250 isn't a 5KHz, 6.5KHz, or 7.5KHz step and therefore
        # isn't valid. (Steps obtained from the User Manual, pg 81.)
        unused.append(freq == 148034250)

    for i in range(channels):
        text_tag = f.read(12)
        if text_tag[0] == 0xff:
            no_text_tag.append(True)
            labels.append('')
        else:
            no_text_tag.append(False)
            text_tag = text_tag.decode('ascii')
            labels.append(text_tag)
        

for i in range(channels):
    memory_slot = (100 * (i//channels_per_bank)) + (i%channels_per_bank)
    print(f"memory[{i}] {memory_slot:03d} {freqs[i]:9d}MHz {labels[i]}")
    print(sectionA[i].hex())
    print(f"mode   {mode_map[modes[i]]}")
    print(f"l/o    {lockout[i]}")
    print(f"atten  {atten[i]}")
    print(f"delay  {delay[i]}")
    print(f"notext {no_text_tag[i]}")
    print(f"unused {unused[i]}")
    print("-"*10)
