# pro93-talk

Talk to RadioShack/GRE Pro93 Scanners (RS Cat No 20-523).

Many, many thanks to [tk92](http://parnass.com/tk92/index.html) by Bob Parnass
for providing information on how to setup the serial port and initiate
communications.

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
* TalkGroup Something? (808 bytes)
* TalkGroup Slot labels (12 bytes \* 1000)
* Scanner settings (unsure; havn't decoded)
  * The limit search label is here (confirmed)
  * I _think_ that the bank labels are here
  * There is an extra 12 spaces which might be a label for something?
  * Limit search upper and lower limits (confirmed)
  * Priority channel (confirmed)

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

### Trunking Something?

808 bytes of something? In my dump it's as follows

    ff00
    8253 3400 x 10
    ffff x 80
    ff00
    64d6 0600 d6dc 0600
    ffff x 96
    ff01
    4ce2 0800
    ffff x 98
    ff00
    ffff x 100

### TalkGroup Text Tags

12 bytes of ASCII text. 12 0xff bytes represents an unset text-tag.
