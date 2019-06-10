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
* TalkGroup Slot Config (unsure; havn't decoded)
* TalkGroup Slot labels (unsure; havn't decoded)
* Scanner settings (unsure; havn't decoded)

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

The Encoded Frequency is the first 3 bytes of a 4-byte little-endian encoded integer. The encoded frequency
can be multiplied by 250 to get the display frequency. `090909` is an invalid step and used as a marker for
when a frequency isn't set.

### Memory Slot Labels

12 bytes of ASCII text. 12 0xff bytes represents an unset text-tag.
