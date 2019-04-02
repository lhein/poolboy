import json
import time

import dbcontrol # our own db utils file
import constants # our own constants def file
import utils # our own utils file

import paho.mqtt.client as mqtt

# create the db tables if not existing
dbcontrol.readyDB()

# start mqtt client
client = mqtt.Client('TEMPERATURE-PROCESSOR')

# Set the username and password for the MQTT client
client.username_pw_set(constants.MQTT_USER, constants.MQTT_PASSWD)

def storeClimateData(sensor, timestamp, temp, humidity, battery_status):
    print("storing data: " + sensor + " / " + timestamp + " / " + temp + " / " + humidity + " / " + battery_status)
    if humidity == constants.SENSOR_NO_DATA:
        # 1wire sensor data
        dbcontrol.storeTemperature(sensor, timestamp, temp)
        dbcontrol.raiseEvent(timestamp, constants.EVENT_TYPE_DEVICE_STATE, constants.EVENT_PRIORITY_INFO, 'Sensor ' + sensor + ' meldet eine Temperatur von ' + temp + ' Grad.')
    else:
        # 433Mhz sensor data
        dbcontrol.storeClimate(sensor, timestamp, temp, humidity, battery_status)
        dbcontrol.raiseEvent(timestamp, constants.EVENT_TYPE_DEVICE_STATE, constants.EVENT_PRIORITY_INFO, 'Sensor ' + sensor + ' meldet eine Temperatur von ' + temp + ' Grad. Luftfeuchtigkeit liegt bei ' + humidity + ' Prozent. Der Batteriestatus ist ' + battery_status + '.')

    # check battery status and raise alarm if needed
    if battery_status.strip().upper() != constants.SENSOR_BATTERY_STATUS_OK:
        # raise battery alarm
        dbcontrol.raiseEvent(timestamp, constants.EVENT_TYPE_DEVICE_STATE, constants.EVENT_PRIORITY_WARNING, 'Sensor ' + sensor + ' meldet eine schwache Batterie! (Status: ' + battery_status + ') Bitte ggf. austauschen!')
        utils.sendAlert(sensor, 'Achtung! Batteriestatus: ' + battery_status + '!')

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(constants.MQTT_TOPIC_TEMPS)
 
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    data = str(msg.payload)
    data = data.replace("b'", '')
    data = data.replace("'", '')
    sensorData = json.loads(data)
    sensor = sensorData[constants.SENSOR_ID_KEY]
    time = sensorData[constants.SENSOR_TIME_KEY]
    temp = sensorData[constants.SENSOR_TEMP_KEY]
    hum = str(sensorData[constants.SENSOR_HUM_KEY])
    bat = sensorData[constants.SENSOR_BAT_KEY]
    storeClimateData(sensor, time, temp, hum, bat)

def on_log(client, userdata, level, buf):
    for msg in userdata:
        print(msg)
    print(buf)

client.on_connect = on_connect
client.on_message = on_message
#client.on_log     = on_log

# wait until mysql and other mandatory deps started up
utils.waitSeconds(30)

# connect to the mqtt server
client.connect(constants.MQTT_SERVER, constants.MQTT_PORT, 60)

# process messages
client.loop_forever()

# finally disconnect
client.disconnect()

