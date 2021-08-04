#!/usr/bin/python3

import paho.mqtt.client as mqtt
import subprocess

broker_address = "home.local"
prefix = "pictureframe/"
subprocess.call("ddcutil setvcp D6 1 && ddcutil setvcp 10 100", shell=True)

def on_message(client, userdata, message):
    decoded = str(message.payload.decode("utf-8"))
    print("message received", decoded)
    print("message topic =", message.topic)
    
    if message.topic == prefix + "commands":
        if decoded == "monitor:on":
            print("Turning monitor on")
            client.publish(prefix + "monitor", "on")
            subprocess.call("ddcutil setvcp D6 1 && ddcutil setvcp 10 100", shell=True)
        elif decoded == "monitor:off":
            print("Turning monitor off")
            client.publish(prefix + "monitor", "off")
            subprocess.call("ddcutil setvcp D6 4", shell=True)
        elif decoded == "power:off":
            print("Turning power off")
            client.publish(prefix + "power", "off")
            subprocess.call("sudo reboot", shell=True)

client = mqtt.Client("P1")
client.on_message = on_message
client.connect(broker_address)
client.subscribe(prefix + "#")
client.publish(prefix + "state", "on")
client.publish(prefix + "monitor", "on")
client.publish(prefix + "power", "on")
client.loop_forever()
