import json

import dbcontrol # our own db utils file
import constants # our own constants def file
import utils # our own utils file

import paho.mqtt.client as mqtt

def storeClimateData(sensor, timestamp, temp, humidity, battery_status):
    if hum == constants.SENSOR_NO_DATA:
        # 1wire sensor data
        dbcontrol.storeTemperature(sensor, timestamp, temp)
        dbcontrol.raiseEvent(timestamp, constants.EVENT_TYPE_DEVICE_STATE, constants.EVENT_PRIORITY_INFO, 'Sensor ' + sensor + ' meldet eine Temperatur von ' + temp + ' Grad.')
    else:
        # 433Mhz sensor data
        dbcontrol.storeClimate(sensor, timestamp, temp, humidity, battery_status)
        dbcontrol.raiseEvent(timestamp, constants.EVENT_TYPE_DEVICE_STATE, constants.EVENT_PRIORITY_INFO, 'Sensor ' + sensor + ' meldet eine Temperatur von ' + str(temp) + ' Grad. Luftfeuchtigkeit liegt bei ' + str(humidity) + ' Prozent. Der Batteriestatus ist ' + battery_status + '.')

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
    sensorData = json.loads(data)
    storeClimateData(sensorData[constants.SENSOR_ID_KEY], constants.SENSOR_TIME_KEY, constants.SENSOR_TEMP_KEY, constants.SENSOR_HUM_KEY, constants.SENSOR_BAT_KEY)

# wait until mysql and other mandatory deps started up
utils.waitSeconds(30)

# create the db tables if not existing
dbcontrol.readyDB()

# start mqtt client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
 
client.connect(constants.MQTT_SERVER, 1883, 60)
 
# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()

