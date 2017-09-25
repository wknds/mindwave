# module: pyserial

import serial
import datetime
import threading

# Byte codes
SYNC = '\xaa'
EXCODE = '\x55'

POOR_SIGNAL = '\x02'
ATTENTION = '\x04'
RAW_8BIT = '\x80'

ATTENTION_IO = '\x11'

class Headset:
    def __init__(self):
        self.parser = Parser(self)
        self.poor_signal_quality = 200
        self.attention = 0
        self.raw = 0
        
    def start(self):
        self.parser.start()

    def stop(self):
        self.parser.stop = 1

class Parser(threading.Thread):

    def __init__(self, headset):
        self.headset = headset
        self.stop = 0
        threading.Thread.__init__(self)
        
    def run(self):
        self.parse()
        
    def parse(self):
        # Serial Stream
        ser = serial.Serial('/dev/rfcomm0', 9600)
        # Clear serial buffer
        ser.read(ser.inWaiting())

        ser.write(ATTENTION_IO)

        found = False
        buffer = ''

        
        
        while self.stop != 1:
            t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            msg = "[" + str(t) + "] "
            if ser.read(1) == SYNC and ser.read(1) == SYNC:
                plength = ser.read(1)
                plength_int = int(plength.encode('hex'), 16)
                if plength_int >= 170:
                    msg += "Error: PLENGTH too large. Packet will be dropped.\n"
                    continue
                msg += "Packet header found. PLENGTH: " + str(plength_int) + " Bytes\n"
                payload = ser.read(plength_int)
                checksum = ser.read(1)
                val = sum(int(b.encode('hex'),16) for b in payload[:])
                val &= 0xff # take the lowest 8 bits
                val = ~val & 0xff
                if val == int(checksum.encode('hex'),16):
                    msg += "Checksum verified. Valid packet.\n"
                    #print msg
                    xcodeCnt = 0
                    self.parsePayload(payload)
                else:
                    msg += "Checksum verfication failed. Invalid packet dropped.\n"
                    continue
                continue
            else:
                continue

    # parse payload
    def parsePayload(self, payload):
        while payload:
            xcodeCnt = 0
            try:
                code, payload = payload[0], payload[1:]
            except IndexError:
                pass
            while code == EXCODE:
                xcodeCnt += 1
                try:
                    code, payload = payload[0], payload[1:]
                    
                except IndexError:
                    pass
            if xcodeCnt == 0:
                if ord(code) <= 0x7F: # Now a Single-Byte value is following:
                    try:
                        value, payload = payload[0], payload[1:]
                    except IndexError:
                        pass
                    if code == POOR_SIGNAL:
                        self.headset.poor_signal_quality = ord(value)
                        #print "POOR_SIGNAL Quality: " + str(ord(value))
                    elif code == ATTENTION:
                        self.headset.attention = ord(value)
                        print str(self.headset.attention)
                else:
                    try:
                        value, payload = payload[0], payload[1:]
                    except IndexError:
                        pass
                    if code == RAW_8BIT:
                        raw = (ord(payload[0]) << 8) | ord(payload[1])
                        if raw > 32767:
                            raw = raw - 65536
                        self.headset.raw = raw
                        try:
                            payload = payload[2:]
                        except IndexError:
                            pass
                        
                    
            break
