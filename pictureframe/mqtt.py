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
            client.publish(prefix + "monitor", "on", retain=True)
            subprocess.call("ddcutil setvcp D6 1 && ddcutil setvcp 10 100", shell=True)
        elif decoded == "monitor:off":
            print("Turning monitor off")
            client.publish(prefix + "monitor", "off", retain=True)
            subprocess.call("ddcutil setvcp D6 4", shell=True)
        elif decoded == "power:off":
            print("Turning power off")
            client.publish(prefix + "power", "off", retain=True)
            subprocess.call("sudo reboot", shell=True)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(prefix + "#")
    client.publish(prefix + "state", "on", retain=True)
    client.publish(prefix + "monitor", "on", retain=True)
    client.publish(prefix + "power", "on", retain=True)

def on_disconnect(client, userdata, rc):
    client.reconnect()

client = mqtt.Client("P1")
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

client.connect(broker_address)
client.loop_forever()
