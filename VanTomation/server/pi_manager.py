import time
import subprocess

from base import SenderReceiver, logger


class PIManager(SenderReceiver):
    def __init__(self):
        SenderReceiver.__init__(self, "Pi")
        subprocess.call("gpio write 0 0", shell=True)
        subprocess.call("gpio write 7 0", shell=True)
        subprocess.call("gpio mode 0 out", shell=True)
        subprocess.call("gpio mode 7 out", shell=True)


    def broadcast_received(self, broadcast):
        if broadcast.destination == "Locks" and broadcast.prop == "State":
            logger.debug("Pi received command %s", broadcast.value)
            
            port = 7 if broadcast.value == "L" else 0
            subprocess.call("gpio mode %d out" % port, shell=True)
            subprocess.call("gpio write %d 1" % port, shell=True)
            time.sleep(0.3)
            subprocess.call("gpio write %d 0" % port, shell=True)
            time.sleep(0.2)
            subprocess.call("gpio write %d 1" % port, shell=True)
            time.sleep(0.3)
            subprocess.call("gpio write %d 0" % port, shell=True)
