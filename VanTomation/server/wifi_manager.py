import threading
import time
import traceback
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
                status = subprocess.check_output('wpa_cli -i wlan1 status', shell=True)
                status = {l.split('=', 1)[0]: l.split('=', 1)[1] for l in status.splitlines()}
                self.add_broadcast(None, "SSID", status.get('ssid'))
                self.add_broadcast(None, "IP", status.get('ip_address'))

                scan = subprocess.check_output('wpa_cli -i wlan1 scan_results', shell=True).splitlines()[1:]
                self.add_broadcast(None, "Scan", [l.split('\t') for l in scan])

            except Exception, e:
                logger.debug("Exception: %s", e)

            time.sleep(10)


    def broadcast_received(self, broadcast):
        if broadcast.destination == self.name and broadcast.prop == "Add":
            network_data = broadcast.value
            logger.info("Adding network %s", network_data)
            network_number = subprocess.check_output('wpa_cli -i wlan1 add_network', shell=True).strip(" \r\n")
            subprocess.check_output('wpa_cli -i wlan1 set_network ' + network_number + ' ssid \'"' + network_data[0] + '"\'', shell=True)
            if network_data[1]:
                subprocess.check_output('wpa_cli -i wlan1 set_network ' + network_number + ' psk \'"' + network_data[1] + '"\'', shell=True)
            else:
                subprocess.check_output('wpa_cli -i wlan1 set_network ' + network_number + ' key_mgmt NONE', shell=True)
            subprocess.check_output('wpa_cli -i wlan1 enable_network ' + network_number, shell=True)
            subprocess.check_output('wpa_cli -i wlan1 save_config', shell=True)

        elif broadcast.destination == self.name and broadcast.prop == "Enable":
            network_data = broadcast.value
            networks = subprocess.check_output('wpa_cli -i wlan1 list_networks', shell=True).splitlines()[1:]
            for line in networks:
                components = line.split("\t")
                if network_data[0] == components[1]:
                    network_number = components[0]
                    subprocess.check_output("wpa_cli -i wlan1 %s_network %s" % ("enable" if network_data[1] else "disable", network_number), shell=True)
                    subprocess.check_output('wpa_cli -i wlan1 save_config', shell=True)
                    break
