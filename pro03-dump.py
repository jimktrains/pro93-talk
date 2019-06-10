#!/usr/bin/evn python3

import serial
import time
import sys
import datetime

serial_options = {
    'port':'/dev/ttyUSB0',
    'baudrate':4800,
    'bytesize':8,
    'parity':'E',
    'stopbits':2,
    'timeout':None,
    'xonxoff':False,
    'rtscts':False,
    'dsrdtr':True
}
with serial.Serial(**serial_options) as port:
    port.write(b'\xcd')
    time.sleep(0.1)
    echo = port.read()
    if echo != b'\xcd':
        print(f"Couldn't read echo of \\xcd; read {echo}")
        sys.exit(1)
    # Preämble?
    print(port.read(50).hex())
    # Some stuff?
    print(port.read(4).hex())

    image = bytearray()
    for i in range(633):
        message = port.read(32)
        image.extend(message)
        print(f"read {i} message")
    # Dump is done backwards for some reason
    image = image[::-1]
    dt = datetime.datetime.now().isoformat()
    with open(f"pro93-dump-{dt}.bin", "wb+") as f:
        f.write(image)
