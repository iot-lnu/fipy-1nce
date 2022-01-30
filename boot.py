import urequests as requests
from network import LTE
from network import WLAN
from simple import MQTTClient
import time
import machine
import pycom
from machine import Pin
import json
import ubinascii

print('Hi, up and running with 1NCE')
pycom.heartbeat(False)
pycom.rgbled(0x7f7f00) # yellow
lte = LTE()

def connect_lte(lte):
    #global lte
    try:
        lte.init()
        apn = 'iot.1nce.net'
        lte.attach(apn=apn)
        print('connecting...')
        time.sleep(1)
        lte.connect()
        pycom.rgbled(0x007f00) # green
    except:
        print('LTE failed')


while not lte.isconnected():
    print("Connecting to LTE ... ")
    connect_lte(lte)
    time.sleep(5)


def sync_time():
    rtc = machine.RTC()
    rtc.ntp_sync("0.se.pool.ntp.org")

sync_time()
# while not rtc.synced():
#     machine.idle()
# print("RTC synced with NTP time")
#adjust your local timezone, by default, NTP time will be GMT
time.timezone(1*60**2) #we are located at GMT+1, thus 2*60*60
