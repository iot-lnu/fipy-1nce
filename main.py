import urequests as requests
from network import LTE
from network import WLAN
from simplemqtt import MQTTClient
import time
import machine
import pycom
from machine import Pin
import json
import _thread

relay = Pin('P23', mode=Pin.OUT, pull=Pin.PULL_DOWN)
relay.value(0)

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

def connect_wifi(wifi_ssid, wifi_pass):
    global wlan
    try:
        wlan = WLAN(mode=WLAN.STA)
        wlan.connect(wifi_ssid, auth=(WLAN.WPA2, wifi_pass), timeout=5000)
    except:
        print('Wifi failed')

def read_config():
    try:
        with open('config.json', 'r') as configfile:
            conf_ = json.load(configfile)
            print('Config loaded')
    except:
        conf_ = None
        print('No config file')
    return conf_

## Not implemented yet ..
##
def update_config():
    with open('config.json', 'w') as configfile:
        configfile.write(json.dumps(wifi_config))
        print('Config file updated.')


while not lte.isconnected():
    print("Connecting to LTE ... ")
    connect_lte(lte)
    time.sleep(5)

config = read_config()

# if config != None:
#     connect_wifi(config['ssid'], config['wifi_pass'])
#
# while not wlan.isconnected():
#     time.sleep(1)
#     print("Connecting to WiFI ... ")

def sync_time():
    rtc = machine.RTC()
    rtc.ntp_sync("0.se.pool.ntp.org")

sync_time()    
# while not rtc.synced():
#     machine.idle()
# print("RTC synced with NTP time")
#adjust your local timezone, by default, NTP time will be GMT
time.timezone(1*60**2) #we are located at GMT+1, thus 2*60*60


def connection_status():
    connection = ""
    try:
        connection += "LTE: " + str(lte.isconnected())
    except:
        pass

    try:
        connection += "\n WiFI: " + str(wlan.isconnected())
    except:
        pass

    return connection


def sub_cb(topic, msg):
    print(msg)
    if msg == b'{"control":"OPEN"}':
        relay.value(1)
        client.publish(topic="relay/status", msg=b'{"status":"open"}')
    if msg == b'{"control":"CLOSE"}':
        relay.value(0)
        client.publish(topic="relay/status", msg=b'{"status":"closed"}')

client = MQTTClient('relay-fipy', config['mqtt_server'], user=config['mqtt_user'], password=config['mqtt_pass'], keepalive=60, ssl=False, port=1883)
client.set_callback(sub_cb)
client.set_last_will("relay/status/device", msg="OFFLINE", retain=True, qos=2)
client.connect()

client.subscribe(topic="relay/control")
client.publish(topic="relay/status/device", msg="ONLINE " + connection_status())

# Send wake up request.
r = requests.get("https://dev0.iotema.io:1880/demo-fipy?state=wake_up " + str(time.localtime() ) )
r.close()

#client.wait_msg() # blocking function
# check relay command

def background_mqtt_check():
    while True:
        client.check_msg()

sub_thread = _thread.start_new_thread(background_mqtt_check,())

def blink_led(blinks):
    for i in range(blinks):
        pycom.rgbled(0x6080BF) # blue
        time.sleep(0.05)
        pycom.rgbled(0x000000) # nul
        time.sleep(0.05)

while True:
    r = requests.get("https://dev0.iotema.io:1880/demo-fipy?state=hearbeat "+ str(time.localtime() ) )
    client.publish(topic="relay/status/heartbeat", msg=str(time.localtime()))
    r.close()
    print(' ... heartbeat ... ' + str(time.localtime()) )
    blink_led(3)
    client.ping()
    time.sleep(10)
