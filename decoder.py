#!/usr/bin/env python3

import struct
import re

mode_map = {
    0:"AM",
    1:"FM",
    # Need to confirm
    2: "MO",
    3:"ED",
}

inv_mode_map = inv_map = {v: k for k, v in mode_map.items()}

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

def set_bits(b, first, last, v):
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
    # TODO TODO TODO This is wrong. It doesn't set 0 bits
    #
    # last + 1 because it's an inclusive it range and the `range` function
    # is exclusive
    #
    # 7-i because we're numbering the bits from mostsig to leastsig
    mask = sum([pow(2,7-i) for i in range(first, last+1)])

    # 7 - last because we're numbering from mostisg to leastsig and
    # we need to shift the result down into the least sig bits.
    return b | ((v & (mask >> (7-last))) << (7 - last))

def make_has_label_bitfield(text_tags):
    bf = bytearray([0x00] * 38)
    for i, text_tag in enumerate(text_tags):
        byi = i // 8
        # lowest chan stored in the LSB
        bti = 7 - (i % 8)

        # can't set a 0 bit right now
        if not text_tag.tag:
            bf[byi] = set_bits(bf[byi], bti, bti, 1)
    return bf


class channel:
    def __init__(self, freq, flags):
        self.freq = freq
        self.flags = flags

    def __repr__(self):
        return f"{self.freq} {self.flags}".strip()

    def encode(self):
        fr = bytearray(self.freq.encode())
        fl = bytearray(self.flags.encode())
        return fr + fl

    @classmethod
    def decode(cls, bs):
        freq = frequency.decode(bs[0:3])
        flags = chan_flags.decode(bytearray([bs[3]]))
        return cls(freq=freq, flags=flags)

class chan_flags:
    def __init__(self, mode=None, atten=None, delay=None, lockout=None):
        self.mode = mode
        self.atten = atten
        self.delay = delay
        self.lockout = lockout

    def __repr__(self):
        r = ''
        if self.mode is not None:
            r += mode_map[self.mode] + " "
        if self.atten:
            r += "A"
        if self.delay:
            r += "D"
        if self.lockout:
            r += "L"
        return r.strip()

    def encode(self):
        bs = bytearray([0])
        bs[0] = set_bits(bs[0], 6, 7, self.mode)
        bs[0] = set_bits(bs[0], 5, 5, 1 if self.atten else 0 )
        bs[0] = set_bits(bs[0], 4, 4, 1 if self.delay else 0 )
        bs[0] = set_bits(bs[0], 3, 3, 1 if self.lockout else 0)
        return bs


    @classmethod
    def decode(cls, bs):
        mode = extract_bits(bs[0], 6, 7)
        atten = 1 == extract_bits(bs[0], 5, 5)
        delay = 1 == extract_bits(bs[0], 4, 4)
        lockout = 1 == extract_bits(bs[0], 3, 3)

        return cls(mode=mode, atten=atten, delay=delay, lockout=lockout)

class frequency:
    def __init__(self, freq, unused):
        self.freq = freq
        self.unused = unused
        # TODO: validate that it's within the freq ranges an steps allowed

    def __repr__(self):
        if self.unused:
            return "-"
        formatted_freq =f"{self.freq/1000000.0:10.05f}"
        r = f"{formatted_freq:>10}" + " "
        return r.strip()

    def encode(self):
        f = int(self.freq / 250)
        bs = bytearray(struct.pack("<L", f))
        del bs[3]
        return bs


    @classmethod
    def decode(cls, bs):
        # 3 bytes of a 4 byte Little Endian Integer are the first 3 bytes
        ef = bytearray(bs[0:3])
        ef.append(0)
        ef = struct.unpack("<L", ef)
        
        # Frequencies are stored in 250Hz increments
        freq = ef[0] * 250

        # Bytes 090909 for the frequency represent an unused frequency.
        # 148.034250 isn't a 5KHz, 6.5KHz, or 7.5KHz step and therefore
        # isn't valid. (Steps obtained from the User Manual, pg 81.)
        #
        # 0xffff is used as the unused in the lockouts section. 4THz isn't
        # within range of this scanner.
        unused = freq in [148034250, 4194303750]

        return cls(freq=freq, unused=unused)


class text_tag:
    def __init__(self, tag):
        self.tag = tag
        if self.tag is None or self.tag == '' or self.tag == '~no tag~':
            self.tag = None

    def __repr__(self):
        if self.tag is None:
            return '~no tag~'
        return self.tag

    def encode(self):
        if self.tag is None:
            return bytes([0xff]) * 12
        # TODO check if lower case or other symbols are allowed
        disallowed_chars = re.compile("[^A-Z0-9 .\-#_@+*&/,]")
        otag = self.tag.upper().strip()
        tag = disallowed_chars.sub(' ', otag)
        # pad with spaces, encode, and trim, this _must_ always be exactly 12
        # bytes of ascii text, unless the first byte is 0ff.
        tag = f"{tag:12}"[0:12]
        if otag != tag.strip():
            print(f"Rewriting tag '{otag}' to '{tag.strip()}'")
        tag = tag.encode('ascii')
        return tag

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

    def encode(self):
        bs = bytearray(struct.pack("<H", self.tgid))
        return bs

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

