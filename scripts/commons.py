import time
from datetime import datetime
from constants import SENSOR_NO_DATA, TEMP_CELSIUS

#SENSOR_NO_DATA = -999.0
#TEMP_CELSIUS = "C"

# sleeps for the given amount of secs
def waitSeconds(secs):
    time.sleep(secs)

# converts Fahrenheit values to Celsius
def convertFahrenheit2Celsius(tempF):
    tempC = float(tempF-32)
    tempC = tempC*(5/9)
    tempC = float('%.1f'%tempC)
    return tempC

# converts Celsius values to Fahrenheit
def convertCelsius2Fahrenheit(tempC):
    tempF = float(tempC)*(9/5)
    tempF = tempF+32
    tempF = float('%.1f'%tempF)
    return tempF

def convertTemperatureTo(value, sysUnit):
    if sysUnit == TEMP_CELSIUS:
        return convertFahrenheit2Celsius(float(value))
    else:
        return convertCelsius2Fahrenheit(float(value))

# returns the current time as a String of format "YYYY-mm-dd HH:MM:SS"
def getCurrentTimestampAsString():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# calculate if we are inside the filter schedule time window
def insideFilterSchedule(scheduledStart, scheduledStop, currentTime):
    time_start = currentTime.replace(hour=int(scheduledStart.split(':')[0]), minute=int(scheduledStart.split(':')[1]))
    time_stop  = currentTime.replace(hour=int(scheduledStop.split(':')[0]), minute=int(scheduledStop.split(':')[1]))
    return currentTime >= time_start and currentTime <= time_stop

# calculates the duration in minutes between two timestamps in the specific format
def calculateDurationInMinutes(later, earlier):
    if later == '' or earlier == '':
        return 0;
    delta = datetime.strptime(later, '%Y-%m-%d %H:%M:%S')-datetime.strptime(earlier, '%Y-%m-%d %H:%M:%S')
    return int(delta.total_seconds() / 60)

# determines if Frost Mode should be enabled
def shouldFrostModeBeActive(frostModeActive, frostModeEnableLimit, frostModeDisableLimit, vorlauf, ruecklauf, solar):
    temp = 999

    print("Check Frostmode Conditions...")
    print("Wassertemp Vorlauf: " + str(vorlauf))
    print("Wassertemp Ruecklauf: " + str(ruecklauf))
    print("Lufttemp Solar: " + str(solar))

    if vorlauf != SENSOR_NO_DATA and vorlauf < temp:
        temp = vorlauf

    if ruecklauf != SENSOR_NO_DATA and ruecklauf < temp:
        temp = ruecklauf

    if solar != SENSOR_NO_DATA and solar < temp:
        temp = solar

    if frostModeActive:
        print("Frostmodus deaktivieren?")
        print(str(temp) + " >= " + str(frostModeDisableLimit) + " -> Frostmode Limit")
        return temp != SENSOR_NO_DATA and temp >= frostModeDisableLimit
    else:
        print("Frostmodus aktivieren?")
        print(str(temp) + " <= " + str(frostModeEnableLimit))
        return temp == 999 or (temp != 999 and temp <= frostModeEnableLimit)

# determines if Cooler Mode should be enabled
def isCoolingRequired(maxPoolTemp, fromPoolWaterTemp, poolWaterTemp, coolerEnableDelta):
    waterTemp = 0.0

    if fromPoolWaterTemp == SENSOR_NO_DATA and \
        poolWaterTemp == SENSOR_NO_DATA:
        return False # no sensor data - do not enable solar for cooling
    else:
        if poolWaterTemp != SENSOR_NO_DATA:
            waterTemp = poolWaterTemp # water temp measured inside pool has prio
        else:
            waterTemp = fromPoolWaterTemp

    print("Prüfung ob Kühlung notwendig...")
    print("Max. Pooltemperatur: " + str(maxPoolTemp))
    print("Akt. Pooltemperatur: " + str(waterTemp))
    print(str(waterTemp) + " > " + str(maxPoolTemp) + " + " + str(coolerEnableDelta))
    return waterTemp > maxPoolTemp + coolerEnableDelta

# determines if current temps allow a cooling of the pool water
def isCoolingPossible(fromPoolWaterTemp, fromSolarWaterTemp, solarAbsorberTemp, poolWaterTemp, coolerEnableDelta):
    fromSolar = 0.0
    toSolar = 0.0

    if fromSolarWaterTemp == SENSOR_NO_DATA and solarAbsorberTemp == SENSOR_NO_DATA:
        return False  # no sensor data - do disable solar
    elif fromPoolWaterTemp == SENSOR_NO_DATA and poolWaterTemp == SENSOR_NO_DATA:
        return False  # no sensor data - do disable solar
    else:
        if poolWaterTemp != SENSOR_NO_DATA:
            toSolar = poolWaterTemp
        else:
            toSolar = fromPoolWaterTemp
            
        if solarAbsorberTemp != SENSOR_NO_DATA:
            fromSolar = solarAbsorberTemp
        else:
            fromSolar = fromSolarWaterTemp

    print("Prüfung ob Kühlung möglich...")
    print("Pool: " + str(toSolar))
    print("Solar: " + str(fromSolar))
    print(str(fromSolar) + " < " + str(toSolar) + " - " + str(coolerEnableDelta))
    return fromSolar < toSolar - coolerEnableDelta

# determine if we have enough heat on solar panels to enable heating if needed
def shouldSolarBeActivated(maxPoolTemp, solarEnableDelta, solarAbsorberTemp, fromPoolWaterTemp, poolWaterTemp):
    delta = 0.0
    waterTemp = 0.0

    if fromPoolWaterTemp == SENSOR_NO_DATA and poolWaterTemp == SENSOR_NO_DATA:
        return False  # no sensor data - do not enable solar
    else:
        if poolWaterTemp != SENSOR_NO_DATA:
            waterTemp = poolWaterTemp
        else:
            waterTemp = fromPoolWaterTemp

        if solarAbsorberTemp != SENSOR_NO_DATA:
            delta = solarAbsorberTemp - waterTemp
            print("Check Solar Enable Conditions...")
            print("Wassertemp Pool: " + str(waterTemp))
            print("Temp Solar: " + str(solarAbsorberTemp))
            print("Maximal gewünschte Wassertemperatur: " + str(maxPoolTemp))
            if (waterTemp >= maxPoolTemp):
                print("Optimale Wassertemperatur erreicht! Kein Heizen notwendig!")
                return False
            print("Delta: " + str(delta) + " (" + str(solarEnableDelta) + ")")
            return delta >= float(solarEnableDelta)
        else:
            # no sensor data from solar absorber
            return False

# determine the solar absorber runtime in minutes
def getSolarRuntimeInMinutes(solarLaunchTime, currentTime):
    print("SolarLaunchTime: " + solarLaunchTime)
    print("CurrentTime: " + currentTime)
    print("Runtime: " + str(calculateDurationInMinutes(currentTime, solarLaunchTime)))
    return calculateDurationInMinutes(currentTime, solarLaunchTime)

# determines if the blocking period for a solar absorber state switch has been reached
def isSolarMinimalRuntimeReached(minRuntimeInMinutes, currentSolarRuntime):
    print("MIN: " + str(minRuntimeInMinutes))
    print("CURRENT: " + str(currentSolarRuntime))
    if currentSolarRuntime < minRuntimeInMinutes:
        print('Minimale Solarlaufzeit noch nicht erreicht. Abschaltung nicht möglich.')
    return currentSolarRuntime >= minRuntimeInMinutes

# determine if we should enable solar absorbers because no effective heating is possible
def shouldSolarBeDeactivated(poolWaterTemp, fromPoolWaterTemp, solarAbsorberTemp, fromSolarWaterTemp, solarDisableDelta):
    delta = 0.0
    fromSolar = 0.0
    toSolar = 0.0

    if fromSolarWaterTemp == SENSOR_NO_DATA and solarAbsorberTemp == SENSOR_NO_DATA:
        return True  # no sensor data - do disable solar
    elif fromPoolWaterTemp == SENSOR_NO_DATA and poolWaterTemp == SENSOR_NO_DATA:
        return True  # no sensor data - do disable solar
    else:
        if poolWaterTemp != SENSOR_NO_DATA:
            toSolar = poolWaterTemp
        else:
            toSolar = fromPoolWaterTemp

        if fromSolarWaterTemp != SENSOR_NO_DATA:
            fromSolar = fromSolarWaterTemp
        else:
            fromSolar = solarAbsorberTemp

        delta = fromSolar - toSolar
        print("Wassertemp Vorlauf: " + str(toSolar))
        print("Wassertemp Ruecklauf: " + str(fromSolar))
        print("Delta: " + str(delta) + " (" + str(solarDisableDelta) + ")")
        return delta <= float(solarDisableDelta)
