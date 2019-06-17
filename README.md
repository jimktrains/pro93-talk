# pro93-talk

Talk to RadioShack/GRE Pro93 Scanners (RS Cat No 20-523).

Many, many thanks to [tk92](http://parnass.com/tk92/index.html) by Bob Parnass
for providing information on how to setup the serial port and initiate
communications.

## Applications

### pro93-dump

Dumps an image of the pro93's memory to a file.

### pro93-write

Writes the contents of an image to the pro93.

### pro93-dump-explore

Decodes an image and writes a summary to standard out.  Also writes out
CSVs of the channels and bank names.  CSVs of options is a TODO.

### pro93-dump-create

Takes a base image, the channel csv, and the bank name csv and produced a new
image.

### encode-freq

Utility that takes the (or a list of) image-format frequency and prints the
corropsonding frequncy and flags.

### encode-freq

Takes a frequncy in MHz and produces the image-formatted value.

## Serial Setup

4800 baud, 8 bit data, even parity, 2 stop bits, xon/xoff off, RTS/CTS off, DSR/DTR on

## Trigger Scanner to Send an Image

A byte of 0xCD will trigger the scanner to dump an image and will be reflected
back.

The image is preceded by a 54 byte preämble consisting of 50 bytes of 0xAD
followed by 0x01991352.

## Image Format

The image is sent in reverse order (e.g. first byte received is the last byte
of the image) and is 20256 bytes long.

* Memory Slot config (4 bytes * 300)
* Memory Slot labels (12 bytes * 300)
* TalkGroup Slot Config (((100\*2 bytes) + 24) \* 10)
* Search Group Lockouts (4 \* ((50 \* 4) + 2))
* TalkGroup Slot labels (12 bytes \* 1000)
* CB Lockout (40 \* 1 byte)
* Unsure? (64 bytes)
* Marine Lockout (60 \* 1 byte)
* Unsure?  (4 bytes)
* Limit Search text (12 bytes)
* Bank Text (10 \* 12 bytes)
* Unsure? (12 bytes)
* Unsure? (38 bytes)
* Limit Search Limits (2 * 4 bytes)
* Priority channel (4 bytes)
* Unsure (46 bytes)

### Memory Slot Config

```
|0       1       2       3       |
|01234567012345670123456701234567|
|Encoded Frequency          LDAMM|

L = Lock Out
D = Delay
A = Attenuated
MM = Mode
```

| Mode | MM Value |
|------|----------|
| AM   | 0b00 (0) |
| FM   | 0b01 (1) |
| Motorola (need to confirm) | 0b10 (2) |
| EDACS | 0b11 (2) |

The Encoded Frequency is the first 3 bytes of a 4-byte little-endian encoded
integer. The encoded frequency can be multiplied by 250 to get the display
frequency. `090909` is an invalid step and used as a marker for when a
frequency isn't set.

### Memory Slot Labels

12 bytes of ASCII text. 12 0xff bytes represents an unset text-tag.

### TalkGroup IDs

2 bytes (Little Endian encoded unsigned short) for each of the 100 talkgroups
in each bank, followed by 24 bytes per bank. (All-in-all 224 bytes per bank.)

In my dump, each bank is followed by 

    000000000000000000647c01c0c71800d007000000000000

I'm not sure what this is? Perhaps the fleetmap is in here somewhere?

### Search Channel Lockout

The search channel lock out has `ffXXYY...YY` where `XX` is the number of
lockouts and each YYYYYYYY quartet is a frequency that is locked out. Note that
old locked-out frequencies may not actually removed from the list, the number
of lockouts may be decremented.

The ordering seems to be

1) Police/Fire (SR2)
2) Aircraft (SR3)
3) HAM (SR4)
4) Limit (SR5) (need to confirm)


### TalkGroup Text Tags

12 bytes of ASCII text. 12 0xff bytes represents an unset text-tag.

### CB Lockout

Each CB channel is represented by 1 byte. 4th MSB is lockout, bottom 2 LSB are
mode. I assume attenuation and delay are in their usual spots.

### Channel Name Set

38 bytes (really 37.5 for 300 bits) of 1-bit flags (0=custom name) if the
channel has a custom name.  Channels are stored with the lowest in the lsb,
e.g. if the first byte is 0x7E => 11101110 => channel 0 and 4 have custom text tags.

     76543210
     11101110

### Unsure?

26 bytes, not sure?

### Marine Lockout

Same encoding as the CB lockout.  Note that Channels 2,3,4 aren't mapped (and
aren't part of the search bank at all).

### Unsure?

4 bytes, not sure?

### Limit Search text

12 bytes

### Bank Text

10 sets of 12 bytes, defaults to spaces, not 0xff like for other tags. (I
presume it's always "shown" but spaces make it invisible.

### Unsure?

12 spaces? I'm not sure what this is the text tag for.

### Unsure?

38 bytes, not sure?

### Limit Search Limits

4 bytes for each of the lower and then the upper limit.

### Priority channel

4 bytes for the priority frequency

### Scan channels selected

2 bytes of 1-bit fields, 1 = selected. Lowest channel in LSB. e.g: A203 =>
10100010 00000011 which means channels 1, 5, 7, 8 and 9 are selected

    76543210 XXXXXX98
    10100010 00000011


### Unsure?
44 bytes, not sure?

## Example

See
[pro93-dump-2019-06-13T05:09:06.494256.parsed](./pro93-dump-2019-06-13T05:09:06.494256.parsed)
for an example of the output of the pro93-dump-explore program.

## Mystery and Outstanding

This diff was obtained from two sequential dumps from the scanner with no changes in between via

    diff <(xxd -c 12 pro93-dump-2019-06-12T23:09:17.548718.bin) <(xxd -c 12 pro93-dump-2019-06-12T23:24:28.168973.bin)

An subsequent dump was identical to pro93-dump-2019-06-12T23:24:28.168973.bin

    diff <(xxd -c 12 pro93-dump-2019-06-12T23:24:28.168973.bin) <(xxd -c 12 pro93-dump-2019-06-12T23:29:47.925511.bin) 

I'm not sure what these values represent.

    1681c1681
    < 00004ec0: 0005 0009 1407 90e0 0209 0092  ............
    ---
    > 00004ec0: 0505 0009 1407 90e0 0209 0092  ............
    1683c1683
    < 00004ed8: 0708 f0d9 0809 c8df 0289 6309  ..........c.
    ---
    > 00004ed8: 0708 f0d9 0809 a8e1 0289 4a09  ..........J.

I'm also not sure what all of the "Unsure" sections are for, but at this point
I'm willing to move forward with writing something to generate an image and
upload it.
