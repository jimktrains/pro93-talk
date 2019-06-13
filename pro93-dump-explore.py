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

# CB and Marine search are channelized and handled seperatly
search_groups = 4
search_lockout_max = 50
search_lockout_count = []
search_lockout_freq = []

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
        # end? Could the sub bank text tag be in here? those normally have
        # text or 0xff though.
        if ip == (tg_mem_per_bank - 1):
            bs = f.read(24)

    for i in range(search_groups):
        # Toss the 0xff away
        bs = f.read(1)
        
        # Gets the number of lockouts
        bs = f.read(1)
        search_lockout_count.append(int(bs[0]))

        freqs = []
        for j in range(search_lockout_max):
            bs = f.read(4)
            freqs.append(decoder.freq_memory.decode(bs))
        search_lockout_freq.append(freqs)


    for i in range(talkgroups):
        bs = f.read(12)
        tg_text_tags.append(decoder.text_tag.decode(bs))

for i in range(channels):
    memory_slot = decoder.index_to_memory_slot(i, channels_per_bank, bank_radix)
    print(f"memory[{i}] {memory_slot:03d} {memory[i]} {text_tags[i]}")

for i in range(talkgroups):
    tg_id = decoder.index_to_tg_memory_slot(i, tg_mem_per_sub_bank, tg_sub_banks_per_bank)
    print(f"{tg_id} {tg_memory[i]} {tg_text_tags[i]}")

for i in range(search_groups):
    lockouts = ", ".join([f"{f}" for f in search_lockout_freq[i] if not f.unused])
    print(f"SR{i+2} {search_lockout_count[i]:02} {lockouts}")
