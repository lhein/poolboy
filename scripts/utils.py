from datetime import datetime
import time
import json

import constants # our own constants
import dbcontrol # our db logic
import gpioutils # our gpio helpers

import paho.mqtt.client as mqtt #import the client

# start mqtt client
client = mqtt.Client('ALERT-BOT')

# Set the username and password for the MQTT client
client.username_pw_set(constants.MQTT_USER, constants.MQTT_PASSWD)

def convertFahrenheit2Celsius(tempF):
    tempC = tempF-32
    tempC = tempC*(5/9)
    tempC = '%.1f'%tempC
    return tempC

def getCurrentTimestampAsString():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# calculate if we are inside the filter schedule time window
def insideFilterSchedule():
    schedStart = dbcontrol.getScheduledFilterStartTime()
    schedStop = dbcontrol.getScheduledFilterStopTime()

    currentTime    = datetime.now()
    time_start = currentTime.replace(hour=int(schedStart.split(':')[0]), minute=int(schedStart.split(':')[1]))
    time_stop  = currentTime.replace(hour=int(schedStop.split(':')[0]), minute=int(schedStop.split(':')[1]))

    return currentTime >= time_start and currentTime <= time_stop

def calculateDurationInMinutes(later, earlier):
    delta = datetime.strptime(later, '%Y-%m-%d %H:%M:%S')-datetime.strptime(earlier, '%Y-%m-%d %H:%M:%S')
    return int(delta.total_seconds() / 60)

def maxDailyFilterRuntimeReached():
    gpioutils.init()

    daily = int(dbcontrol.getPumpDailyRuntime())
    maxDaily = int(dbcontrol.getPumpDailyRuntimeMax())

    if gpioutils.getFilterPumpState() == constants.ON:
        # wenn filter aktiv => dailyRuntime + (now - launchtime) >= MaxRuntime
        pumpTime = calculateDurationInMinutes(getCurrentTimestampAsString(), dbcontrol.getPumpLaunchTime())
        return (daily + pumpTime) >= maxDaily
    else:
        # wenn filter inaktiv => dailyRuntime >= MaxRuntime
        return  daily >= maxDaily

def shouldFrostModeBeEnabled():
    gpioutils.init()

    frostModeEnableLimit = float(dbcontrol.getFrostModeActivationLimit())
    frostModeDisableLimit = frostModeEnableLimit + 2 # reactivation if 2 degrees above frost limit
    frostModeActive = gpioutils.getFrostModeState() == constants.ON

    vorlauf = float(dbcontrol.getLastestSensorTemperature(constants.SENSOR_VORLAUF_ID))
    ruecklauf = float(dbcontrol.getLastestSensorTemperature(constants.SENSOR_RUECKLAUF_ID))
    solar = float(dbcontrol.getLastestSensorTemperature(constants.SENSOR_SOLAR_ID))

    print("Check Frostmode Conditions...")
    print("Wassertemp Vorlauf: " + str(vorlauf))
    print("Wassertemp Ruecklauf: " + str(ruecklauf))
    print("Lufttemp Solar: " + str(solar))

    limit = frostModeEnableLimit
    temp = vorlauf;

    if ruecklauf < temp:
        temp = ruecklauf
    if solar < temp:
        temp = solar

    if frostModeActive:
        print("Frostmodus deaktivieren?")
        print(str(temp) + " >= " + str(frostModeDisableLimit) + " -> Frostmode Limit + 2 Grad")
        return temp >= frostModeDisableLimit        
    else:
        print("Frostmodus aktivieren?")
        print(str(temp) + " <= " + str(frostModeEnableLimit))
        return temp != constants.SENSOR_NO_DATA and temp <= frostModeEnableLimit

def isCoolingRequired():
    maxPoolTemp = float(dbcontrol.getMaximumPoolTemperature())
    fromPoolWaterTemp = float(dbcontrol.getLastestSensorTemperature(constants.SENSOR_VORLAUF_ID))
    poolWaterTemp = float(dbcontrol.getLastestSensorTemperature(constants.SENSOR_POOLWATER_ID)) # fallback if filter water temp is not available
    waterTemp = 0.0
    if fromPoolWaterTemp == constants.SENSOR_NO_DATA and poolWaterTemp == constants.SENSOR_NO_DATA:
        return False # no sensor data - do not enable solar
    else:
        if fromPoolWaterTemp != constants.SENSOR_NO_DATA:
            waterTemp = fromPoolWaterTemp
        if poolWaterTemp > waterTemp:
            waterTemp = poolWaterTemp
    print("Prüfung ob Kühlung notwendig...")
    print("Max. Pooltemperatur: " + str(maxPoolTemp))
    print("Akt. Pooltemperatur: " + str(waterTemp))
    print(str(waterTemp) + " > " + str(maxPoolTemp) + " + 2 ")
    return waterTemp > maxPoolTemp + 2 # 2 Grad Toleranz

def isCoolingPossible():
    # solar / ruecklauf temp < poolwasser/vorlauf - 2 Grad 
    solarDisableDelta = dbcontrol.getSolarDisableDelta()
    fromSolarWaterTemp = dbcontrol.getLastestSensorTemperature(constants.SENSOR_RUECKLAUF_ID)
    solarAbsorberTemp = dbcontrol.getLastestSensorTemperature(constants.SENSOR_SOLAR_ID) # fallback if from absorber water temp is not available
    fromPoolWaterTemp = dbcontrol.getLastestSensorTemperature(constants.SENSOR_VORLAUF_ID)
    poolWaterTemp = dbcontrol.getLastestSensorTemperature(constants.SENSOR_POOLWATER_ID) # fallback if filter water temp is not available
    delta = 0.0
    fromSolar = 0.0
    toSolar = 0.0
    if fromSolarWaterTemp == constants.SENSOR_NO_DATA and solarAbsorberTemp == constants.SENSOR_NO_DATA:
        return True # no sensor data - do disable solar
    elif fromPoolWaterTemp == constants.SENSOR_NO_DATA and poolWaterTemp == constants.SENSOR_NO_DATA:
        return True # no sensor data - do disable solar
    else:
        if fromPoolWaterTemp != constants.SENSOR_NO_DATA:
            toSolar = fromPoolWaterTemp
        else:
            toSolar = poolWaterTemp
        if fromSolarWaterTemp != constants.SENSOR_NO_DATA:
            fromSolar = fromSolarWaterTemp
        else:
            fromSolar = solarAbsorberTemp
    print("Prüfung ob Kühlung möglich...")
    print("Vorlauf: " + str(toSolar))
    print("Rücklauf: " + str(fromSolar))
    print(str(fromSolar) + " < " + str(toSolar) + " - 2 ")
    return fromSolar < toSolar - 2

def shouldSolarBeActivated():
    maxPoolTemp = float(dbcontrol.getMaximumPoolTemperature())
    solarEnableDelta = dbcontrol.getSolarEnableDelta()
    solarAbsorberTemp = dbcontrol.getLastestSensorTemperature(constants.SENSOR_SOLAR_ID)
    fromPoolWaterTemp = dbcontrol.getLastestSensorTemperature(constants.SENSOR_VORLAUF_ID)
    poolWaterTemp = dbcontrol.getLastestSensorTemperature(constants.SENSOR_POOLWATER_ID) # fallback if filter water temp is not available
    delta = 0.0
    waterTemp = 0.0
    if fromPoolWaterTemp == constants.SENSOR_NO_DATA and poolWaterTemp == constants.SENSOR_NO_DATA:
        return False # no sensor data - do not enable solar
    else:
        if fromPoolWaterTemp != constants.SENSOR_NO_DATA:
            waterTemp = fromPoolWaterTemp
        else:
            waterTemp = poolWaterTemp
        delta = solarAbsorberTemp - waterTemp
        print("Check Solar Enable Conditions...")
        print("Wassertemp Pool: " + str(waterTemp))
        print("Temp Solar: " + str(solarAbsorberTemp))
        print("Maximal gewünschte Wassertemperatur: " + str(maxPoolTemp))
        if (waterTemp >= maxPoolTemp):
            print("Optimale Wassertemperatur erreicht! Kein Heizen notwendig!")
            return False
        print("Delta: " + str(delta) + " (" + str(solarEnableDelta) + ")")
        return delta >=  float(solarEnableDelta)

def getSolarRuntimeInMinutes():
    solarLaunchTime = dbcontrol.getSolarLaunchTime()
    currentTime = getCurrentTimestampAsString()
    runtimeInMinutes = calculateDurationInMinutes(currentTime, solarLaunchTime)
    return runtimeInMinutes

def isSolarMinimalRuntimeReached():
    minRuntimeInMinutes = int(dbcontrol.getMinimalSolarRuntime())
    currentSolarRuntime = getSolarRuntimeInMinutes()
    return currentSolarRuntime >= minRuntimeInMinutes

def shouldSolarBeDeactivated():
    print("Check Solar Disable Conditions...")
    if not isSolarMinimalRuntimeReached():
        print("Mindestlaufzeit Solar noch nicht erreicht!")
        return False

    solarDisableDelta = dbcontrol.getSolarDisableDelta()
    fromSolarWaterTemp = dbcontrol.getLastestSensorTemperature(constants.SENSOR_RUECKLAUF_ID)
    solarAbsorberTemp = dbcontrol.getLastestSensorTemperature(constants.SENSOR_SOLAR_ID) # fallback if from absorber water temp is not available
    fromPoolWaterTemp = dbcontrol.getLastestSensorTemperature(constants.SENSOR_VORLAUF_ID)
    poolWaterTemp = dbcontrol.getLastestSensorTemperature(constants.SENSOR_POOLWATER_ID) # fallback if filter water temp is not available
    delta = 0.0
    fromSolar = 0.0
    toSolar = 0.0
    if fromSolarWaterTemp == constants.SENSOR_NO_DATA and solarAbsorberTemp == constants.SENSOR_NO_DATA:
        return True # no sensor data - do disable solar
    elif fromPoolWaterTemp == constants.SENSOR_NO_DATA and poolWaterTemp == constants.SENSOR_NO_DATA:
        return True # no sensor data - do disable solar
    else:
        if fromPoolWaterTemp != constants.SENSOR_NO_DATA:
            toSolar = fromPoolWaterTemp
        else:
            toSolar = poolWaterTemp
        if fromSolarWaterTemp != constants.SENSOR_NO_DATA:
            fromSolar = fromSolarWaterTemp
        else:
            fromSolar = solarAbsorberTemp
        delta = fromSolar - toSolar
        print("Wassertemp Vorlauf: " + str(toSolar))
        print("Wassertemp Ruecklauf: " + str(fromSolar))
        print("Delta: " + str(delta) + " (" + str(solarDisableDelta) + ")")
        return delta <=  float(solarDisableDelta)

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
    # connect
    client.connect(constants.MQTT_SERVER, constants.MQTT_PORT, 60)
    alert = createAlertMQTTStructure(sender, msg)
    client.publish(constants.MQTT_TOPIC_TEMPS, json.dumps(alert))
    client.loop()
    # finally disconnect
    client.disconnect()


