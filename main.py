import mindwave
import time

headset = mindwave.Headset()

print "********** Start Headset **********"
headset.start()
usr_input = ""
while usr_input != "q":
            usr_input = raw_input("Please enter a command: ")
            if usr_input == "PSQ":
                print "POOR_SIGNAL_QUALITY: " + str(headset.poor_signal_quality)
            elif usr_input == "ATT":
                print "ATTENTION: " + str(headset.attention)
            elif usr_input == "RAW":
                print "RAW: " + str(headset.raw)
            elif usr_input == "RAW*":
                count = 0
                while count != 60:
                    raw = headset.raw
                    while raw > 16000:
                        raw = headset.raw
                    stars = ""
                    for i in xrange(raw):
                        stars += "#"
                    print "[" + stars + "]" + " [" + str(raw) + "]"
                    count += 1
                    time.sleep(0.5)
headset.stop()
print "********** Headset stopped **********"
