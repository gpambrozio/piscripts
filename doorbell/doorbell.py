#!/usr/bin/python3

from gpiozero import PWMLED, Button
from time import sleep
import http.client

led = PWMLED(12)
button = Button(26)

def button_pressed():
    print("Button is pressed")

    print("Taking snapshot")
    conn = http.client.HTTPConnection("localhost:7999")
    conn.request("GET", "/0/action/snapshot")
    r = conn.getresponse()
    print(r.status, r.reason)
    conn.close()

    print("Telling HA")
    conn = http.client.HTTPConnection("home.local:8123")
    conn.request("POST", "/api/webhook/doorbell")
    r = conn.getresponse()
    print(r.status, r.reason)
    conn.close()

button.when_pressed = button_pressed

while True:
    for value in range(0, 100):
        led.value = value / 100
        sleep(0.01)
    for value in range(100, 0, -1):
        led.value = value / 100
        sleep(0.01)
