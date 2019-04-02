import os
import json

import constants # our own constants def file
import utils     # our own utils file

import paho.mqtt.client as mqtt #import the client
 
# local constants only used in this script
ID = 'id'
DEVICE = 'device'

SENSORS = [ { 'id': constants.SENSOR_SOLAR_ID, 'device': constants.SENSOR_SOLAR },
            { 'id': constants.SENSOR_VORLAUF_ID, 'device': constants.SENSOR_VORLAUF },
            { 'id': constants.SENSOR_RUECKLAUF_ID, 'device': constants.SENSOR_RUECKLAUF }, ]

# Aktuelle Kabelbelegung DS18B20 wasserdicht (schwarz.rot,gelb): Schwarz  = GND,  Rot = 3.3V,   Gelb = DATA
# read the value of a w1 sensor
def read_from_w1(sensorid):
    """Reads the temperature from the given w1 bus slave device"""
    sensorpath = "/sys/bus/w1/devices/%s/w1_slave" % sensorid
    cmd = 'cat ' + sensorpath + ' | grep ' + constants.SENSOR_TEMP_KEY + '='
    process = os.popen(cmd)
    rawdata = process.read()
    if not rawdata:
        # either sensor is offline or did not send data
        temp = NO_DATA
    else:
        temp = int(rawdata.split('=')[1])
        temp = temp / 1000;
        temp = '%.1f'%temp
    return temp;

# start mqtt client
client = mqtt.Client('1WIRE-SENSOR-POLLER')

# Set the username and password for the MQTT client
client.username_pw_set(constants.MQTT_USER, constants.MQTT_PASSWD)

# connect
client.connect(constants.MQTT_SERVER, constants.MQTT_PORT, 60)

# read the sensor data
for sensor in SENSORS:
    temp = read_from_w1(sensor[DEVICE])
    msg = utils.createSensorMQTTStructure(sensor[ID])
    msg[constants.SENSOR_TEMP_KEY] = temp;
    client.publish(constants.MQTT_TOPIC_TEMPS, json.dumps(msg))

# finally disconnect
client.disconnect()

