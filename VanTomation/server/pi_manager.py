import glob
import os
import subprocess
import threading
import time

from base import SenderReceiver, logger


# Temperature reading rom https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/software
class PIManager(SenderReceiver):
    def __init__(self):
        SenderReceiver.__init__(self, "Pi")
        subprocess.call("gpio write 0 0", shell=True)
        subprocess.call("gpio write 2 0", shell=True)
        subprocess.call("gpio mode 0 out", shell=True)
        subprocess.call("gpio mode 2 out", shell=True)

        os.system("modprobe w1-gpio")
        os.system("modprobe w1-therm")

        base_dir = "/sys/bus/w1/devices/"
        device_folder = glob.glob(base_dir + "28*")[0]
        self.device_file = device_folder + "/w1_slave"

        self.thread = threading.Thread(target=self.read_temperature_thread)
        self.thread.daemon = True                            # Daemonize thread
        self.thread.start()                                  # Start the execution


    def broadcast_received(self, broadcast):
        if broadcast.destination == "Locks" and broadcast.prop == "State":
            logger.debug("Pi received command %s", broadcast.value)
            
            port = 2 if broadcast.value == "L" else 0
            subprocess.call("gpio mode %d out" % port, shell=True)
            subprocess.call("gpio write %d 1" % port, shell=True)
            time.sleep(0.3)
            subprocess.call("gpio write %d 0" % port, shell=True)
            time.sleep(0.2)
            subprocess.call("gpio write %d 1" % port, shell=True)
            time.sleep(0.3)
            subprocess.call("gpio write %d 0" % port, shell=True)
        
        elif broadcast.destination == "Pi" and broadcast.prop == "DateTime":
            # Date format is 0603232819.58 (see man date)
            subprocess.call("sudo date %s" % broadcast.value, shell=True)

        elif broadcast.destination == "Pi" and broadcast.prop == "TimeZone":
            # TZ is America/Denver
            subprocess.call("sudo timedatectl set-timezone %s" % broadcast.value, shell=True)


    def read_temperature_thread(self):
        while True:
            temp_f = self.read_temp()
            self.add_broadcast(None, "Temperature", temp_f)
            time.sleep(10)


    def read_temp_raw(self):
        f = open(self.device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines


    def read_temp(self):
        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw()

        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            return temp_f
