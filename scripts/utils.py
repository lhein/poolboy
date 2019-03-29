from datetime import datetime
import time
import json
import constants # our own constants
import paho.mqtt.publish as publish

def convertFahrenheit2Celsius(tempF):
    tempC = tempF-32
    tempC = tempC*(5/9)
    tempC = '%.1f'%tempC
    return tempC

def getCurrentTimestampAsString():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def insideFilterSchedule():
#todo
    return True

def maxDailyFilterRuntimeReached():
#todo
    return False

def shouldSolarBeActivated():
#todo Ruecklauf/Solar - Vorlauf > minSolarDelta
    return False

def shouldSolarBeDeactivated():
#todo Ruecklauf/Solar - Vorlauf < hysteresis
    return True 

def waitSeconds(secs):
    time.sleep(secs)

def createSensorMQTTStructure(sensorid):
    return { constants.SENSOR_ID_KEY: sensorid,
             constants.SENSOR_TIME_KEY: getCurrentTimestampAsString(),
             constants.SENSOR_TEMP_KEY: constants.SENSOR_NO_DATA,
             constants.SENSOR_HUM_KEY: constants.SENSOR_NO_DATA,
             constants.SENSOR_BAT_KEY: constants.SENSOR_BATTERY_STATUS_OK }

def createAlertMQTTStructure(sender, alert):
    return { constants.ALERT_SENDER_KEY: sender,
             constants.ALERT_TIME_KEY: getCurrentTimestampAsString(),
             constants.ALERT_MSG_KEY: alert }

def sendAlert(sender, msg):
    alert = createAlertMQTTStructure(sender, msg)
    publish.single(constants.MQTT_TOPIC_ALERTS, json.dumps(alert), hostname=constants.MQTT_SERVER)

