import sys
import os
import json

import dbcontrol # our own db utils file
import constants # our own constants def file
import commons   # our commons lib

from sensor import Sensor

MODEL = 'model'
HUM   = 'humidity'
TEMP  = 'temperature_C'
TEMPF = 'temperature_F'
BAT   = 'battery'
TIME  = 'time'
DEV   = 'device' # currently not evaluated
CH    = 'channel'
MIC   = 'mic'

# read the current weather data (cron start every 10 minutes - abort after 550 sec of 600 sec
process = os.popen('/usr/local/bin/rtl_433 -G -F json -T 100')
s = process.read()

if not s:
    os.system('sudo /usr/sbin/usb_modeswitch -v 0x0bda -p 0x2838 --reset-usb')
    sys.exit(1)

# get the sensors
sensors = dbcontrol.getSensorsForType(constants.SENSOR_TYPE_433MHZ)

# get system temp unit
sysTempUnit = dbcontrol.getSystemTemperatureUnit()

# process <n> lines of json and filter for interesting sensors
lines = s.splitlines()
for line in lines:
    json_obj = json.loads(line)

    # loop the sensors for comparing
    for sensor in sensors:
        if json_obj[MODEL] == sensor.sensor_model and str(json_obj[CH]) == sensor.sensor_channel and json_obj[MIC] == 'CRC':
            # save the data in DB
            if line.find(TEMP) != -1:
                temp = json_obj[TEMP]
            elif line.find(TEMPF) != -1:
                temp = json_obj[TEMPF]
            else:
                # no valid temperature key found
                print("No valid temperature found in sensor data.\n", line)
                continue

            humidity = json_obj[HUM]
            battery_status = json_obj[BAT]
            timestamp = json_obj[TIME]
            sensorid = sensor.sensor_location_id

            # store the data
            dbcontrol.storeClimate(sensorid, timestamp, str(temp), sensor.temperatureunit, humidity, battery_status)

            t = temp
            if sensor.temperatureunit != sysTempUnit:
                if sysTempUnit == constants.TEMP_CELSIUS:
                    t = commons.convertFahrenheit2Celsius(temp)
                else:
                    t = commons.convertCelsius2Fahrenheit(temp)

            dbcontrol.raiseEvent(timestamp, constants.EVENT_TYPE_DEVICE_STATE, constants.EVENT_PRIORITY_INFO, 'Sensor ' + sensorid + ' reports a temperature of ' + str(t) + ' °' + sysTempUnit + '. Humidity is at ' + str(humidity) + '%. Batteries are ' + battery_status + '.')

            # check battery status and raise alarm if needed
            if battery_status.strip().upper() != constants.SENSOR_BATTERY_STATUS_OK:
                # raise battery alarm
                dbcontrol.raiseEvent(timestamp, constants.EVENT_TYPE_DEVICE_STATE, constants.EVENT_PRIORITY_WARNING, 'Sensor ' + sensorid + ' reports a weak battery! (Status: ' + battery_status + ') Please replace the battery!')


