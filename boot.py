from network_connector import NetworkConnector
#from lib import logging
import urequests as requests
from network import LTE
from network import WLAN
from simple import MQTTClient
import time
import machine
import pycom
import json
import ubinascii

print('Hi, up and running with 1NCE')
pycom.heartbeat(False)
pycom.rgbled(0x7f7f00) # yellow

#logging.basic_config(level=logging.INFO)

connector = NetworkConnector()
connector.connect()


def sync_time():
    rtc = machine.RTC()
    rtc.ntp_sync("0.se.pool.ntp.org")

sync_time()
# while not rtc.synced():
#     machine.idle()
# print("RTC synced with NTP time")
#adjust your local timezone, by default, NTP time will be GMT
time.timezone(1*60**2) #we are located at GMT+1, thus 2*60*60
