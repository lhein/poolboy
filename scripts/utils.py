from datetime import datetime

import commons   # our basic logic module
import constants # our own constants
import dbcontrol # our db logic
import gpioutils # our gpio helpers
from filterschedule import FilterSchedule # the filter schedule item class

# calculate if we are inside the filter schedule time window
def insideFilterSchedule():
    schedules = dbcontrol.getFilterSchedules()
    for schedule in schedules:
        currentTime    = datetime.now()
        if commons.insideFilterSchedule(schedule.startTime, schedule.endTime, currentTime):
           return True
    return False

# determines if Frost Mode should be enabled
def shouldFrostModeBeActive():
    gpioutils.init()
    frostModeEnableLimit = float(dbcontrol.getFrostModeActivationLimit())
    frostModeDisableLimit = frostModeEnableLimit + 2 # deactivation if 2 degrees above frost limit
    frostModeActive = gpioutils.getFrostModeState() == constants.ON
    vorlauf = float(dbcontrol.getLastestSensorTemperature(constants.SENSOR_VORLAUF_ID))
    ruecklauf = float(dbcontrol.getLastestSensorTemperature(constants.SENSOR_RUECKLAUF_ID))
    solar = float(dbcontrol.getLastestSensorTemperature(constants.SENSOR_SOLAR_ID))
    return commons.shouldFrostModeBeActive(frostModeActive, frostModeEnableLimit, frostModeDisableLimit, vorlauf, ruecklauf, solar)

# determines if Cooler Mode should be enabled
def isCoolingRequired():
    maxPoolTemp = float(dbcontrol.getMaximumPoolTemperature())
    fromPoolWaterTemp = float(dbcontrol.getLastestSensorTemperature(constants.SENSOR_VORLAUF_ID))
    poolWaterTemp = float(dbcontrol.getLastestSensorTemperature(constants.SENSOR_POOLWATER_ID)) # fallback if filter water temp is not available
    coolerEnableDelta = float(dbcontrol.getCoolerEnableDelta())
    return commons.isCoolingRequired(maxPoolTemp, fromPoolWaterTemp, poolWaterTemp, coolerEnableDelta)

# determines if current temps allow a cooling of the pool water
def isCoolingPossible():
    fromSolarWaterTemp = dbcontrol.getLastestSensorTemperature(constants.SENSOR_RUECKLAUF_ID)
    solarAbsorberTemp = dbcontrol.getLastestSensorTemperature(constants.SENSOR_SOLAR_ID) # fallback if from absorber water temp is not available
    fromPoolWaterTemp = dbcontrol.getLastestSensorTemperature(constants.SENSOR_VORLAUF_ID)
    poolWaterTemp = dbcontrol.getLastestSensorTemperature(constants.SENSOR_POOLWATER_ID) # fallback if filter water temp is not available
    coolerEnableDelta = float(dbcontrol.getCoolerEnableDelta())
    return commons.isCoolingPossible(fromPoolWaterTemp, fromSolarWaterTemp, solarAbsorberTemp, poolWaterTemp, coolerEnableDelta)

# determine the solar absorber runtime in minutes
def getSolarRuntimeInMinutes():
    solarLaunchTime = dbcontrol.getSolarLaunchTime()
    currentTime = commons.getCurrentTimestampAsString()
    return commons.getSolarRuntimeInMinutes(solarLaunchTime, currentTime)

# determines if the blocking period for a solar absorber state switch has been reached
def isSolarMinimalRuntimeReached():
    minRuntimeInMinutes = int(dbcontrol.getMinimalSolarRuntime())
    currentSolarRuntime = getSolarRuntimeInMinutes()
    return commons.isSolarMinimalRuntimeReached(minRuntimeInMinutes, currentSolarRuntime)

# determine if we have enough heat on solar panels to enable heating if needed
def shouldSolarBeActivated():
    maxPoolTemp = float(dbcontrol.getMaximumPoolTemperature())
    solarEnableDelta = dbcontrol.getSolarEnableDelta()
    solarAbsorberTemp = dbcontrol.getLastestSensorTemperature(constants.SENSOR_SOLAR_ID)
    fromPoolWaterTemp = dbcontrol.getLastestSensorTemperature(constants.SENSOR_VORLAUF_ID)
    poolWaterTemp = dbcontrol.getLastestSensorTemperature(constants.SENSOR_POOLWATER_ID) # fallback if filter water temp is not available
    return commons.shouldSolarBeActivated(maxPoolTemp, solarEnableDelta, solarAbsorberTemp, fromPoolWaterTemp, poolWaterTemp)

# determine if we should enable solar absorbers because no effective heating is possible
def shouldSolarBeDeactivated():
    print("Check Solar Disable Conditions...")
    if (insideFilterSchedule() or dbcontrol.getFilterOverrideMode() == constants.ON_STRING):
        solarDisableDelta = dbcontrol.getSolarDisableDelta()
        fromSolarWaterTemp = dbcontrol.getLastestSensorTemperature(constants.SENSOR_RUECKLAUF_ID)
        solarAbsorberTemp = dbcontrol.getLastestSensorTemperature(constants.SENSOR_SOLAR_ID) # fallback if from absorber water temp is not available
        fromPoolWaterTemp = dbcontrol.getLastestSensorTemperature(constants.SENSOR_VORLAUF_ID)
        poolWaterTemp = dbcontrol.getLastestSensorTemperature(constants.SENSOR_POOLWATER_ID) # fallback if filter water temp is not available
        return commons.shouldSolarBeDeactivated(poolWaterTemp, fromPoolWaterTemp, solarAbsorberTemp, fromSolarWaterTemp, solarDisableDelta)
    else:
        return True
