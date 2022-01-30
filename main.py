
relay = Pin('P23', mode=Pin.OUT, pull=Pin.PULL_DOWN)
relay.value(0)



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


config = read_config()

# if config != None:
#     connect_wifi(config['ssid'], config['wifi_pass'])
#
# while not wlan.isconnected():
#     time.sleep(1)
#     print("Connecting to WiFI ... ")


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
    blink_led(3)
    if msg == b'{"control":"OPEN"}':
        relay.value(1)
        client.publish(topic="relay/status", msg=b'{"status":"open"}')
    if msg == b'{"control":"CLOSE"}':
        relay.value(0)
        client.publish(topic="relay/status", msg=b'{"status":"closed"}')

def connect_mqtt():
    global client
    client = MQTTClient('fipy_device_relay', config['mqtt_server'], user=config['mqtt_user'], password=config['mqtt_pass'], keepalive=120, ssl=False, port=1883)
    client.set_callback(sub_cb)
    client.set_last_will("relay/status/device", msg="OFFLINE", retain=True, qos=0)
    client.connect()
    client.subscribe(topic="relay/control")
    client.publish(topic="relay/status/device", msg="ONLINE " + connection_status())

# Send wake up request.
r = requests.get("https://dev0.iotema.io:1880/demo-fipy?state=wake_up " + str(time.localtime() ) )
r.close()

def blink_led(blinks):
    for i in range(blinks):
        pycom.rgbled(0x6080BF) # blue
        time.sleep(0.05)
        pycom.rgbled(0x000000) # nul
        time.sleep(0.05)

while True:
    #r = requests.get("https://dev0.iotema.io:1880/demo-fipy?state=hearbeat "+ str(time.localtime() ) )
    #r.close()
    #client.publish(topic="relay/status/heartbeat", msg=str(time.localtime()))
    #print(' ... heartbeat ... ' + str(time.localtime()) )
    #client.ping()
    try:
        client.check_msg()
        if time.time() % 60 == 0:
            client.publish(topic="relay/status/heartbeat", msg=str(time.localtime()))
            #client.ping()
        time.sleep(0.1)
    except:
        print('reconnecting ..')
        connect_mqtt()
        time.sleep(1)
    #time.sleep(0.1)
