import os

import dbcontrol # our own db utils file
import constants # our own constants def file
import commons   # out commons lib

from sensor import Sensor    # provides the sensor class

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
        temp = constants.SENSOR_NO_DATA
    else:
        temp = int(rawdata.split('=')[1])
        temp = temp / 1000;
        temp = '%.1f'%temp
    return temp;

def storeClimateData(sensor, temp, unit):
    timestamp = commons.getCurrentTimestampAsString()
    dbcontrol.storeTemperature(sensor, timestamp, temp, unit)

    # get system temp unit
    sysTempUnit = dbcontrol.getSystemTemperatureUnit()

    # do conversion if required for more readable events
    t = temp
    if unit != sysTempUnit:
        if sysTempUnit == constants.TEMP_CELSIUS:
            t = commons.convertFahrenheit2Celsius(temp)
        else:
            t = commons.convertCelsius2Fahrenheit(temp)

    dbcontrol.raiseEvent(timestamp, constants.EVENT_TYPE_DEVICE_STATE, constants.EVENT_PRIORITY_INFO, 'Sensor ' + sensor + ' reports a temperature of ' + str(t) + ' °' + sysTempUnit + '.')

# get the sensors
sensors = dbcontrol.getSensorsForType(constants.SENSOR_TYPE_1WIRE)

# read the sensor data
for sensor in sensors:
    temp = read_from_w1(sensor.sensor_address)
    storeClimateData(sensor.sensor_location_id, temp, sensor.temperatureunit)

