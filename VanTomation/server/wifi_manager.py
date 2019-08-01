import threading
import time
import traceback
import re
import subprocess

from base import SenderReceiver, logger


class WiFiManager(SenderReceiver):
    def __init__(self):
        SenderReceiver.__init__(self, "WiFi")
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()
        logger.debug("Started")


    def run(self):
        """ Method that runs forever """
        time.sleep(2)   # Give some time for others to start working too...
        while True:
            try:
                ip_stats = subprocess.check_output('ping -q -c 2 8.8.8.8 || true', shell=True).splitlines()[3:]
                ping_time = None
                for ip_stat in ip_stats:
                    ping = re.search(r'rtt min/avg/max/mdev = [\d.]+/([\d.]+)/[\d.]+/[\d.]+ ms', ip_stat, re.S)
                    if ping is not None:
                        ping_time = float(ping.group(1))
                        break
                self.add_broadcast(None, "Ping", ping_time)
                time.sleep(10 if ping_time is None else 5)

            except Exception, e:
                logger.debug("Exception: %s", e)
