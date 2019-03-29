import sys
import os
import json

import constants # our own constants def file
import utils # our own utils file

import paho.mqtt.publish as publish

MODEL = 'model'
HUM   = 'humidity'
TEMP  = 'temperature_C'
TEMPF = 'temperature_F'
BAT   = 'battery'
TIME  = 'time'
DEV   = 'device'

# read the current weather data (cron start every 10 minutes - abort after 550 sec of 600 sec
process = os.popen('/usr/local/bin/rtl_433 -G -F json -T 100')
s = process.read()

if not s:
    os.system('sudo /usr/sbin/usb_modeswitch -v 0x0bda -p 0x2838 --reset-usb')
    sys.exit(1)

# process <n> lines of json and filter for interesting sensors
lines = s.splitlines()
for line in lines:
    json_obj = json.loads(line)
    # default outdoor and poolwater temperature grabbed from weather station
    if json_obj[MODEL] == constants.SENSOR_MODEL_VENICE:
        # save the data in DB
        temp = utils.convertFahrenheit2Celsius(json_obj[TEMPF])
        humidity = json_obj[HUM]
        battery_status = json_obj[BAT]
        timestamp = json_obj[TIME]
        sensorid = ''
        if json_obj[DEV] == constants.SENSOR_POOLWATER:
            sensorid = constants.SENSOR_POOLWATER_ID
        elif json_obj[DEV] == constants.SENSOR_OUTDOOR:
            sensorid = constants.SENSOR_OUTDOOR_ID
        elif json_obj[DEV] == constants.SENSOR_TECHNIK:
            sensorid = constants.SENSOR_TECHNIK_ID
        elif json_obj[DEV] == constants.SENSOR_GARAGE:
            sensorid = constants.SENSOR_GARAGE_ID
        elif json_obj[DEV] == constants.SENSOR_GREENHOUSE:
            sensorid = constants.SENSOR_GREENHOUSE_ID
        elif json_obj[DEV] == constants.SENSOR_GARDENHOUSE:
            sensorid = constants.SENSOR_GARDENHOUSE_ID

        if sensorid != '':
            msg = utils.createSensorMQTTStructure(sensorid)
            msg[constants.SENSOR_TEMP_KEY] = temp;
            msg[constants.SENSOR_HUM_KEY] = humidity;
            msg[constants.SENSOR_BAT_KEY] = battery_status;
            msg[constants.SENSOR_TIME_KEY] = timestamp;
            publish.single(constants.MQTT_TOPIC_TEMPS, json.dumps(msg), hostname=constants.MQTT_SERVER)


