import sys
import os
import time
import RPi.GPIO as GPIO

import dbcontrol # our own db utils file
import constants # our own constants def file
import utils # our own utils file

# for debug purposes
def setupGPIOPorts():
    GPIO.setup(constants.GPIO_AUTOMATIC, GPIO.OUT, initial=constants.ON)
    GPIO.setup(constants.GPIO_PUMP, GPIO.OUT, initial=constants.OFF)
    GPIO.setup(constants.GPIO_SOLAR, GPIO.OUT, initial=constants.OFF)
    GPIO.setup(constants.GPIO_FILTER_MAN, GPIO.OUT, initial=constants.OFF)
    GPIO.setup(constants.GPIO_SOLAR_MAN, GPIO.OUT, initial=constants.OFF)
    GPIO.setup(constants.GPIO_WINTER_MODE, GPIO.OUT, initial=constants.OFF)

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
    deactivateManualFilterMode()
    deactivateManualSolarMode()
    deactivateAutomaticMode()
    deactivateWinterMode()

###############
# FILTER PUMP #
###############
def activateFilterPump():
    if getFilterPumpState() == constants.OFF:
        writeToGPIO(constants.GPIO_PUMP, constants.ON)
        # insert events into event table
        dbcontrol.raiseEvent(utils.getCurrentTimestampAsString(), constants.EVENT_TYPE_DEVICE_STATE, constants.EVENT_PRIORITY_INFO, 'Filterpumpe wurde aktiviert.')

def deactivateFilterPump():
    if getFilterPumpState() == constants.ON:
        writeToGPIO(constants.GPIO_PUMP, constants.OFF)
        # insert events into event table
        dbcontrol.raiseEvent(utils.getCurrentTimestampAsString(), constants.EVENT_TYPE_DEVICE_STATE, constants.EVENT_PRIORITY_INFO, 'Filterpumpe wurde deaktiviert.')

def getFilterPumpState():
    return readFromGPIO(constants.GPIO_PUMP)

#########
# SOLAR #
#########
def activateSolar():
    if getSolarState() == constants.OFF:
        writeToGPIO(constants.GPIO_SOLAR, constants.ON)
        # insert events into event table
        dbcontrol.raiseEvent(utils.getCurrentTimestampAsString(), constants.EVENT_TYPE_DEVICE_STATE, constants.EVENT_PRIORITY_INFO, 'Solarabsorber wurde aktiviert.')

def deactivateSolar():
    if getSolarState() == constants.ON:
        writeToGPIO(constants.GPIO_SOLAR, constants.OFF)
        # insert events into event table
        dbcontrol.raiseEvent(utils.getCurrentTimestampAsString(), constants.EVENT_TYPE_DEVICE_STATE, constants.EVENT_PRIORITY_INFO, 'Solarabsorber wurde deaktiviert.')

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

def deactivateAutomaticMode():
    if getAutomaticModeState() == constants.ON:
        writeToGPIO(constants.GPIO_AUTOMATIC, constants.OFF)
        # insert events into event table
        dbcontrol.raiseEvent(utils.getCurrentTimestampAsString(), constants.EVENT_TYPE_CONTROLLER_MODE, constants.EVENT_PRIORITY_INFO, 'Automatikbetrieb wurde deaktiviert.')

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

def deactivateManualFilterMode():
    if getManualFilterModeState() == constants.ON:
        writeToGPIO(constants.GPIO_FILTER_MAN, constants.OFF)
        # insert events into event table
        dbcontrol.raiseEvent(utils.getCurrentTimestampAsString(), constants.EVENT_TYPE_CONTROLLER_MODE, constants.EVENT_PRIORITY_INFO, 'Manueller Pumpenbetrieb wurde deaktiviert.')

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

def deactivateManualSolarMode():
    if getManualSolarModeState() == constants.ON:
        writeToGPIO(constants.GPIO_SOLAR_MAN, constants.OFF)
        # insert events into event table
        dbcontrol.raiseEvent(utils.getCurrentTimestampAsString(), constants.EVENT_TYPE_CONTROLLER_MODE, constants.EVENT_PRIORITY_INFO, 'Manueller Solarbetrieb wurde deaktiviert.')

def getManualSolarModeState():
    return readFromGPIO(constants.GPIO_SOLAR_MAN)

###############
# WINTER MODE #
###############
def activateWinterMode():
    if getWinterModeState() == constants.OFF:
        writeToGPIO(constants.GPIO_WINTER_MODE, constants.ON)
        # insert events into event table
        dbcontrol.raiseEvent(utils.getCurrentTimestampAsString(), constants.EVENT_TYPE_CONTROLLER_MODE, constants.EVENT_PRIORITY_INFO, 'Wintermodus wurde aktiviert.')

def deactivateWinterMode():
    if getWinterModeState() == constants.ON:
        writeToGPIO(constants.GPIO_WINTER_MODE, constants.OFF)
        # insert events into event table
        dbcontrol.raiseEvent(utils.getCurrentTimestampAsString(), constants.EVENT_TYPE_CONTROLLER_MODE, constants.EVENT_PRIORITY_INFO, 'Wintermodus wurde deaktiviert.')

def getWinterModeState():
    return readFromGPIO(constants.GPIO_WINTER_MODE)

