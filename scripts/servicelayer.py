import constants # our own constants def file
import dbcontrol # our own db utils file
import gpioutils
import utils # our own utils file

def init():
    # init gpio
    gpioutils.init()

def isAutomaticModeActive():
    return gpioutils.getAutomaticModeState() == constants.ON or dbcontrol.getAutomaticMode() == constants.ON_STRING

def isEmergencyModeActive():
    return dbcontrol.getEmergencyMode() == constants.ON_STRING

def isFrostModeActive():
    return dbcontrol.getFrostMode() == constants.ON_STRING

def isFilterPumpActive():
    return gpioutils.getFilterPumpState() == constants.ON

def isSolarActive():
    return gpioutils.getSolarState() == constants.ON

def isCoolerModeActive():
    return gpioutils.getCoolerModeState() == constants.ON_STRING

def isManualSolarModeActive():
    return gpioutils.getManualSolarModeState() == constants.ON_STRING

def isManualFilterModeActive():
    return gpioutils.getManualFilterModeState() == constants.ON_STRING

def activateEmergencyMode():
    gpioutils.activateEmergencyMode()
    if isFilterPumpActive():
        deactivateFilterPump()
    if isSolarActive():
        forceDeactivateSolar()
    deactivateAutomaticMode()
    deactivateManualFilterMode()
    deactivateManualSolarMode()

def deactivateEmergencyMode():
    gpioutils.deactivateEmergencyMode()

def activateAutomaticMode():
    if gpioutils.getAutomaticModeState() == constants.OFF:
        gpioutils.activateAutomaticMode()
        print("AutomaticMode activated")
    # remember we are in automatic mode
    dbcontrol.updateAutomaticMode(constants.ON_STRING)

def deactivateAutomaticMode():
    if gpioutils.getAutomaticModeState() == constants.ON:
        gpioutils.deactivateAutomaticMode()
        print("AutomaticMode deactivated")
    # remember we are in automatic mode
    dbcontrol.updateAutomaticMode(constants.OFF_STRING)

def activateCoolerMode():
    print("Cooler Mode activated")
    gpioutils.activateCoolerMode()

def deactivateCoolerMode():
    print("Cooler Mode deactivated")
    gpioutils.deactivateCoolerMode()

def activateFrostMode():
    print("FrostMode activated")
    if not isFilterPumpActive():
        activateFilterPump()
    if not isSolarActive():
        activateSolar()

def deactivateFrostMode():
    print("FrostMode deactivated")
    gpioutils.deactivateFrostMode()

def shouldFrostModeBeActivated():
    return utils.shouldFrostModeBeActive()

def activateFilterPump():
    if gpioutils.getFilterPumpState() == constants.OFF:
        print("Activate Filter Pump")
        gpioutils.activateFilterPump()

def deactivateFilterPump():
    if gpioutils.getFilterPumpState() == constants.ON:
        print("Deactivate Filter Pump")
        gpioutils.deactivateFilterPump()

def activateSolar():
    print("Activate Solar")
    gpioutils.activateSolar()

def forceDeactivateSolar():
    print("Deactivate Solar")
    gpioutils.deactivateSolar()
    return True

def deactivateSolar():
    if utils.isSolarMinimalRuntimeReached():
        print("Deactivate Solar")
        gpioutils.deactivateSolar()
        return True
    else:
        print("Solar Min Runtime not reached yet...")
        return False

def shouldSolarBeActivated():
    return utils.shouldSolarBeActivated()

def shouldSolarBeDeactivated():
    return utils.shouldSolarBeDeactivated()

def isSolarMinRuntimeReached():
    return utils.isSolarMinimalRuntimeReached()

def activateManualFilterMode():
    if gpioutils.getManualFilterModeState() == constants.ON_STRING:
        print("Activate Manual Filter Mode")
        deactivateAutomaticMode()
        gpioutils.activateManualFilterMode()

def deactivateManualFilterMode():
    if gpioutils.getManualFilterModeState() == constants.OFF_STRING:
        print("Deactivate Manual Filter Mode")
        gpioutils.deactivateManualFilterMode()

def activateManualSolarMode():
    if gpioutils.getManualSolarModeState() == constants.ON_STRING:
        print("Activate Manual Solar Mode")
        deactivateAutomaticMode()
        gpioutils.activateManualSolarMode()

def deactivateManualSolarMode():
    if gpioutils.getManualSolarModeState() == constants.OFF_STRING:
        print("Deactivate Manual Solar Mode")
        gpioutils.deactivateManualSolarMode()

def isInsideFilterSchedule():
    return utils.insideFilterSchedule()

def isCoolingRequired():
    return utils.isCoolingRequired()

def isCoolingPossible():
    return utils.isCoolingPossible()

def isHeatingOverrideModeActive():
    return dbcontrol.getHeatingOverrideMode() == constants.ON_STRING

