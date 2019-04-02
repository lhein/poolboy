import sys
import os
import time
import RPi.GPIO as GPIO

import dbcontrol # our own db utils file
import constants # our own constants def file
import utils # our own utils file

# for debug purposes
def setupGPIOPorts():
    GPIO.setup(constants.GPIO_EMERGENCY_MODE, GPIO.OUT, initial=constants.OFF)
    GPIO.setup(constants.GPIO_AUTOMATIC, GPIO.OUT, initial=constants.OFF)
    GPIO.setup(constants.GPIO_PUMP, GPIO.OUT, initial=constants.OFF)
    GPIO.setup(constants.GPIO_COOLER_MODE, GPIO.OUT, initial=constants.OFF)
    GPIO.setup(constants.GPIO_SOLAR, GPIO.OUT, initial=constants.OFF)
    GPIO.setup(constants.GPIO_FILTER_MAN, GPIO.OUT, initial=constants.OFF)
    GPIO.setup(constants.GPIO_SOLAR_MAN, GPIO.OUT, initial=constants.OFF)
    GPIO.setup(constants.GPIO_FROST_MODE, GPIO.OUT, initial=constants.OFF)

def init():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
   
# write a value to the GPIO
def writeToGPIO(gpio, value):
    GPIO.output(gpio, value)

# read a value from the GPIO
def readFromGPIO(gpio):
    GPIO.setup(gpio, GPIO.OUT)
    return GPIO.input(gpio)

# read a value from the GPIO
def readFromGPIO_old(gpio):
    # we can't read from gpio directly otherwise its state changes to high/off always
    with os.popen('/usr/bin/gpio -g read ' + str(gpio)) as process:
        s = process.read().strip()

        if not s:
            return constants.OFF

        return int(s)

# helper function to initialize all gpio pins needed by turning them off
def deactivateAll():
    deactivateFilterPump()
    deactivateSolar()
    deactivateCoolerMode()
    deactivateManualFilterMode()
    deactivateManualSolarMode()
    deactivateAutomaticMode()
    deactivateFrostMode()
    deactivateEmergencyMode()

###############
# FILTER PUMP #
###############
def activateFilterPump():
    if getFilterPumpState() == constants.OFF:
        # if solar is active we need to do the protocol and reset
        if getSolarState() == constants.ON:
            dbcontrol.updateSolarRuntime()
            dbcontrol.setSolarLaunchTime(utils.getCurrentTimestampAsString())
        writeToGPIO(constants.GPIO_PUMP, constants.ON)
        # remember the start datetime
        dbcontrol.setPumpLaunchTime(utils.getCurrentTimestampAsString())
        # insert events into event table
        dbcontrol.raiseEvent(utils.getCurrentTimestampAsString(), constants.EVENT_TYPE_DEVICE_STATE, constants.EVENT_PRIORITY_INFO, 'Filterpumpe wurde aktiviert.')
        # log action for later statistics
        dbcontrol.logAction(utils.getCurrentTimestampAsString(), constants.ACTION_TYPE_HW_STATUS, constants.ACTION_SOURCE_PUMP, constants.ACTION_ENABLE)

def deactivateFilterPump():
    if getFilterPumpState() == constants.ON:
        # if solar is active we need to do the protocol and reset
        if getSolarState() == constants.ON:
            dbcontrol.updateSolarRuntime()
        writeToGPIO(constants.GPIO_PUMP, constants.OFF)
        # calculate pump runtime and add to overall, finally reset the pump time config value
        dbcontrol.updatePumpRuntime()
        # insert events into event table
        dbcontrol.raiseEvent(utils.getCurrentTimestampAsString(), constants.EVENT_TYPE_DEVICE_STATE, constants.EVENT_PRIORITY_INFO, 'Filterpumpe wurde deaktiviert.')
        # log action for later statistics
        dbcontrol.logAction(utils.getCurrentTimestampAsString(), constants.ACTION_TYPE_HW_STATUS, constants.ACTION_SOURCE_PUMP, constants.ACTION_DISABLE)

def getFilterPumpState():
    return readFromGPIO(constants.GPIO_PUMP)

#########
# SOLAR #
#########
def activateSolar():
    if getSolarState() == constants.OFF:
        writeToGPIO(constants.GPIO_SOLAR, constants.ON)
        # remember the start datetime
        dbcontrol.setSolarLaunchTime(utils.getCurrentTimestampAsString())
        # insert events into event table
        dbcontrol.raiseEvent(utils.getCurrentTimestampAsString(), constants.EVENT_TYPE_DEVICE_STATE, constants.EVENT_PRIORITY_INFO, 'Solarabsorber wurde aktiviert.')
        # log action for later statistics
        dbcontrol.logAction(utils.getCurrentTimestampAsString(), constants.ACTION_TYPE_HW_STATUS, constants.ACTION_SOURCE_SOLAR, constants.ACTION_ENABLE)

def deactivateSolar():
    if getSolarState() == constants.ON:
        writeToGPIO(constants.GPIO_SOLAR, constants.OFF)
        # calculate solar runtime and add to overall, finally reset the solar time config value
        dbcontrol.updateSolarRuntime()
        # insert events into event table
        dbcontrol.raiseEvent(utils.getCurrentTimestampAsString(), constants.EVENT_TYPE_DEVICE_STATE, constants.EVENT_PRIORITY_INFO, 'Solarabsorber wurde deaktiviert.')
        # log action for later statistics
        dbcontrol.logAction(utils.getCurrentTimestampAsString(), constants.ACTION_TYPE_HW_STATUS, constants.ACTION_SOURCE_SOLAR, constants.ACTION_DISABLE)

def getSolarState():
    return readFromGPIO(constants.GPIO_SOLAR)

##################
# AUTOMATIC MODE #
##################
def activateAutomaticMode():
    if getAutomaticModeState() == constants.OFF:
        writeToGPIO(constants.GPIO_AUTOMATIC, constants.ON)
        # insert events into event table
        dbcontrol.raiseEvent(utils.getCurrentTimestampAsString(), constants.EVENT_TYPE_CONTROLLER_MODE, constants.EVENT_PRIORITY_INFO, 'Automatikbetrieb wurde aktiviert.')
        # log action for later statistics
        dbcontrol.logAction(utils.getCurrentTimestampAsString(), constants.ACTION_TYPE_MODE_SWITCH, constants.ACTION_SOURCE_MODE_AUTOMATIC, constants.ACTION_ENABLE)

def deactivateAutomaticMode():
    if getAutomaticModeState() == constants.ON:
        writeToGPIO(constants.GPIO_AUTOMATIC, constants.OFF)
        # insert events into event table
        dbcontrol.raiseEvent(utils.getCurrentTimestampAsString(), constants.EVENT_TYPE_CONTROLLER_MODE, constants.EVENT_PRIORITY_INFO, 'Automatikbetrieb wurde deaktiviert.')
        # log action for later statistics
        dbcontrol.logAction(utils.getCurrentTimestampAsString(), constants.ACTION_TYPE_MODE_SWITCH, constants.ACTION_SOURCE_MODE_AUTOMATIC, constants.ACTION_DISABLE)

def getAutomaticModeState():
    return readFromGPIO(constants.GPIO_AUTOMATIC)

######################
# MANUAL FILTER MODE #
######################
def activateManualFilterMode():
    if getManualFilterModeState() == constants.OFF:
        writeToGPIO(constants.GPIO_FILTER_MAN, constants.ON)
        # insert events into event table
        dbcontrol.raiseEvent(utils.getCurrentTimestampAsString(), constants.EVENT_TYPE_CONTROLLER_MODE, constants.EVENT_PRIORITY_INFO, 'Manueller Pumpenbetrieb wurde aktiviert.')
        # log action for later statistics
        dbcontrol.logAction(utils.getCurrentTimestampAsString(), constants.ACTION_TYPE_MODE_SWITCH, constants.ACTION_SOURCE_MODE_MANUALFILTER, constants.ACTION_ENABLE)

def deactivateManualFilterMode():
    if getManualFilterModeState() == constants.ON:
        writeToGPIO(constants.GPIO_FILTER_MAN, constants.OFF)
        # insert events into event table
        dbcontrol.raiseEvent(utils.getCurrentTimestampAsString(), constants.EVENT_TYPE_CONTROLLER_MODE, constants.EVENT_PRIORITY_INFO, 'Manueller Pumpenbetrieb wurde deaktiviert.')
        # log action for later statistics
        dbcontrol.logAction(utils.getCurrentTimestampAsString(), constants.ACTION_TYPE_MODE_SWITCH, constants.ACTION_SOURCE_MODE_MANUALFILTER, constants.ACTION_DISABLE)

def getManualFilterModeState():
    return readFromGPIO(constants.GPIO_FILTER_MAN)

#####################
# MANUAL SOLAR MODE #
#####################
def activateManualSolarMode():
    if getManualSolarModeState() == constants.OFF:
        writeToGPIO(constants.GPIO_SOLAR_MAN, constants.ON)
        # insert events into event table
        dbcontrol.raiseEvent(utils.getCurrentTimestampAsString(), constants.EVENT_TYPE_CONTROLLER_MODE, constants.EVENT_PRIORITY_INFO, 'Manueller Solarbetrieb wurde aktiviert.')
        # log action for later statistics
        dbcontrol.logAction(utils.getCurrentTimestampAsString(), constants.ACTION_TYPE_MODE_SWITCH, constants.ACTION_SOURCE_MODE_MANUALSOLAR, constants.ACTION_ENABLE)

def deactivateManualSolarMode():
    if getManualSolarModeState() == constants.ON:
        writeToGPIO(constants.GPIO_SOLAR_MAN, constants.OFF)
        # insert events into event table
        dbcontrol.raiseEvent(utils.getCurrentTimestampAsString(), constants.EVENT_TYPE_CONTROLLER_MODE, constants.EVENT_PRIORITY_INFO, 'Manueller Solarbetrieb wurde deaktiviert.')
        # log action for later statistics
        dbcontrol.logAction(utils.getCurrentTimestampAsString(), constants.ACTION_TYPE_MODE_SWITCH, constants.ACTION_SOURCE_MODE_MANUALSOLAR, constants.ACTION_DISABLE)

def getManualSolarModeState():
    return readFromGPIO(constants.GPIO_SOLAR_MAN)

###############
# FROST MODE #
###############
def activateFrostMode():
    if getFrostModeState() == constants.OFF:
        writeToGPIO(constants.GPIO_FROST_MODE, constants.ON)
        # insert events into event table
        dbcontrol.raiseEvent(utils.getCurrentTimestampAsString(), constants.EVENT_TYPE_CONTROLLER_MODE, constants.EVENT_PRIORITY_INFO, 'Frostschutzmodus wurde aktiviert.')
        # log action for later statistics
        dbcontrol.logAction(utils.getCurrentTimestampAsString(), constants.ACTION_TYPE_MODE_SWITCH, constants.ACTION_SOURCE_MODE_FROST, constants.ACTION_ENABLE)

def deactivateFrostMode():
    if getFrostModeState() == constants.ON:
        writeToGPIO(constants.GPIO_FROST_MODE, constants.OFF)
        # insert events into event table
        dbcontrol.raiseEvent(utils.getCurrentTimestampAsString(), constants.EVENT_TYPE_CONTROLLER_MODE, constants.EVENT_PRIORITY_INFO, 'Frostschutzmodus wurde deaktiviert.')
        # log action for later statistics
        dbcontrol.logAction(utils.getCurrentTimestampAsString(), constants.ACTION_TYPE_MODE_SWITCH, constants.ACTION_SOURCE_MODE_FROST, constants.ACTION_DISABLE)

def getFrostModeState():
    return readFromGPIO(constants.GPIO_FROST_MODE)


###############
# FRIDGE MODE #
###############
def activateCoolerMode():
    if getCoolerModeState() == constants.OFF:
        writeToGPIO(constants.GPIO_COOLER_MODE, constants.ON)
        # insert events into event table
        dbcontrol.raiseEvent(utils.getCurrentTimestampAsString(), constants.EVENT_TYPE_CONTROLLER_MODE, constants.EVENT_PRIORITY_INFO, 'Kuehlungsmodus wurde aktiviert.')
        # log action for later statistics
        dbcontrol.logAction(utils.getCurrentTimestampAsString(), constants.ACTION_TYPE_MODE_SWITCH, constants.ACTION_SOURCE_MODE_COOLER, constants.ACTION_ENABLE)

def deactivateCoolerMode():
    if getCoolerModeState() == constants.ON:
        writeToGPIO(constants.GPIO_COOLER_MODE, constants.OFF)
        # insert events into event table
        dbcontrol.raiseEvent(utils.getCurrentTimestampAsString(), constants.EVENT_TYPE_CONTROLLER_MODE, constants.EVENT_PRIORITY_INFO, 'Kuehlungsmodus wurde deaktiviert.')
        # log action for later statistics
        dbcontrol.logAction(utils.getCurrentTimestampAsString(), constants.ACTION_TYPE_MODE_SWITCH, constants.ACTION_SOURCE_MODE_COOLER, constants.ACTION_DISABLE)

def getCoolerModeState():
    return readFromGPIO(constants.GPIO_COOLER_MODE)


##################
# EMERGENCY MODE #
##################
def activateEmergencyMode():
    if getEmergencyModeState() == constants.OFF:
        writeToGPIO(constants.GPIO_EMERGENCY_MODE, constants.ON)
        # insert events into event table
        dbcontrol.raiseEvent(utils.getCurrentTimestampAsString(), constants.EVENT_TYPE_CONTROLLER_MODE, constants.EVENT_PRIORITY_INFO, 'Not-Aus wurde aktiviert.')
        # log action for later statistics
        dbcontrol.logAction(utils.getCurrentTimestampAsString(), constants.ACTION_TYPE_MODE_SWITCH, constants.ACTION_SOURCE_MODE_EMERGENCY, constants.ACTION_ENABLE)

def deactivateEmergencyMode():
    if getEmergencyModeState() == constants.ON:
        writeToGPIO(constants.GPIO_EMERGENCY_MODE, constants.OFF)
        # insert events into event table
        dbcontrol.raiseEvent(utils.getCurrentTimestampAsString(), constants.EVENT_TYPE_CONTROLLER_MODE, constants.EVENT_PRIORITY_INFO, 'Not-Aus wurde quittiert.')
        # log action for later statistics
        dbcontrol.logAction(utils.getCurrentTimestampAsString(), constants.ACTION_TYPE_MODE_SWITCH, constants.ACTION_SOURCE_MODE_EMERGENCY, constants.ACTION_DISABLE)

def getEmergencyModeState():
    return readFromGPIO(constants.GPIO_EMERGENCY_MODE)

