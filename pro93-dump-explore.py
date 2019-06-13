#!/usr/bin/env python3

import struct
import decoder

bank_radix = 100
banks = 10
channels_per_bank = 30
channels = banks * channels_per_bank
tg_sub_banks_per_bank = 5
tg_mem_per_sub_bank = 20
tg_mem_per_bank = tg_sub_banks_per_bank * tg_mem_per_sub_bank
talkgroups = banks * tg_mem_per_bank

sectionA = []

memory = []
text_tags = []
tg_memory = []
tg_text_tags = []

fn = 'pro93-dump-2019-06-10T13:09:35.841920.bin'
with open(fn, 'rb') as f:

    for i in range(channels):
        bs = f.read(4)
        sectionA.append(bs)
        memory.append(decoder.freq_memory.decode(bs))


    for i in range(channels):
        bs = f.read(12)
        text_tags.append(decoder.text_tag.decode(bs))

    for i in range(talkgroups):
        bs = f.read(2)
        tg_memory.append(decoder.talk_group.decode(bs))

        ip = i % tg_mem_per_bank
        # Not sure what this is, but I needed it in order to get some
        # preëxisting tags to line up.
        # Seems to be 000000000000000000647c01c0c71800d007000000000000
        # for all 10 of my banks.
        # Somewhere in here is the fleetmap? or is it in the 808 bits at the
        # end? Could the sub bank text tag be in here? those normally have
        # text or 0xff though.
        if ip == (tg_mem_per_bank - 1):
            bs = f.read(24)

    # I've no clue what's here?
    # Each of the sub banks can have a text ID.
    # 10 banks * 5 subbanks * 12 bytes = 600 bytes
    # Lots of 0xff in here.
    #
    # ff00
    # 8253 3400 x 10, so this might be some kind of settings for each bank?
    # ffff x 80
    # ff00
    # 64d6 0600 x 2
    # ffff x 96
    # ff01 
    # 4ce2 0800
    # ffff x 98
    # ff00
    # ffff x 100

    bs = f.read(808)

    for i in range(talkgroups):
        bs = f.read(12)
        tg_text_tags.append(decoder.text_tag.decode(bs))

for i in range(channels):
    memory_slot = decoder.index_to_memory_slot(i, channels_per_bank, bank_radix)
    print(f"memory[{i}] {memory_slot:03d} {memory[i]} {text_tags[i]}")

for i in range(talkgroups):
    tg_id = decoder.index_to_tg_memory_slot(i, tg_mem_per_sub_bank, tg_sub_banks_per_bank)
    print(f"{tg_id} {tg_memory[i]} {tg_text_tags[i]}")
