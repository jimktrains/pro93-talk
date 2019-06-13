#!/usr/bin/env python3

import struct

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

class freq_memory:
    def __init__(self, mode, atten, delay, lockout, freq, unused):
        self.mode = mode
        self.atten = atten
        self.delay = delay
        self.lockout = lockout
        self.freq = freq
        self.unused = unused
    def __repr__(self):
        if self.unused:
            return "-"
        formatted_freq =f"{self.freq/1000000.0:10.05f}"
        r = f"{formatted_freq:>10}" + " " 
        if self.mode:
            r += mode_map[self.mode] + " "
        if self.atten:
            r += "A"
        if self.delay:
            r += "D"
        if self.lockout:
            r += "L"
        return r.strip()

    @classmethod
    def decode(cls, bs):
        mode = None
        atten = None
        delay = None
        lockout = None
        if len(bs) == 4:
            mode = extract_bits(bs[3], 6, 7)
            atten = 1 == extract_bits(bs[3], 5, 5)
            delay = 1 == extract_bits(bs[3], 4, 4)
            lockout = 1 == extract_bits(bs[3], 3, 3)

        # 3 bytes of a 4 byte Little Endian Integer are the first 3 bytes
        ef = bytearray(bs[0:3])
        ef.append(0)
        ef = struct.unpack("<L", ef)
        
        # Frequencies are stored in 250Hz increments
        freq = ef[0] * 250

        # Bytes 090909 for the frequency represent an unused frequency.
        # 148.034250 isn't a 5KHz, 6.5KHz, or 7.5KHz step and therefore
        # isn't valid. (Steps obtained from the User Manual, pg 81.)
        unused = freq == 148034250

        return cls(mode=mode, atten=atten, delay=delay, lockout=lockout, freq=freq, unused=unused)


class text_tag:
    def __init__(self, tag):
        self.tag = tag

    def __repr__(self):
        if self.tag is None:
            return '~no tag~'
        return self.tag

    @classmethod
    def decode(cls, tag):
        ttag = None
        if tag[0] != 0xff:
            ttag = tag.decode('ascii')
        return cls(tag=ttag)

class talk_group:
    def __init__(self, tgid):
        self.tgid = tgid
    def __repr__(self):
        return f"{self.tgid:05}"

    @classmethod
    def decode(cls, bs):
        tgid = struct.unpack("<H", bs)[0]
        return cls(tgid=tgid)

def index_to_memory_slot(i, channels_per_bank, bank_radix):
    return (bank_radix * (i//channels_per_bank)) + (i%channels_per_bank)

def index_to_tg_memory_slot(i, tg_mem_per_sub_bank, tg_sub_bank_per_bank):
    tg_mem_per_bank = tg_mem_per_sub_bank * tg_sub_bank_per_bank

    tg_slot_bank = i // tg_mem_per_bank
    tg_sub_bank_mem_slot = i % tg_mem_per_bank
    tg_slot_sub_bank = tg_sub_bank_mem_slot // tg_mem_per_sub_bank
    tg_slot_mem  = tg_sub_bank_mem_slot % tg_mem_per_sub_bank

    return f"{tg_slot_bank}-{tg_slot_sub_bank}-{tg_slot_mem:02}"
