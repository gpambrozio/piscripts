import threading
import time
import traceback
import subprocess

from base import SenderReceiver, logger


class WiFiManager(SenderReceiver):
    def __init__(self):
        SenderReceiver.__init__(self, "Wifi")
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()
        logger.debug("Started")


    def run(self):
        """ Method that runs forever """
        time.sleep(2)   # Give some time for others to start working too...
        while True:
            try:
                status = subprocess.check_output('wpa_cli -i wlan1 status', shell=True)
                status = {l.split('=', 1)[0]: l.split('=', 1)[1] for l in status.splitlines()}
                self.add_broadcast(None, "SSID", status.get('ssid'))
                self.add_broadcast(None, "IP", status.get('ip_address'))

                scan = subprocess.check_output('wpa_cli -i wlan1 scan_results', shell=True)
                scan = [l.split('\t') for l in scan.splitlines()[1:]]
                self.add_broadcast(None, "Scan", scan)

            except Exception, e:
                logger.debug("Exception: %s", e)

            time.sleep(10)
