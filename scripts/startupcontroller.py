import dbcontrol # our own db utils file
import constants # our own constants def file
import utils # our own utils file
import gpioutils # our helper file for gpio access

# init gpio
gpioutils.init()

# on first start we also need to initialize the ports to the correct state
gpioutils.setupGPIOPorts()

# for security reasons disable all gpios
gpioutils.deactivateAll()

# remember the start time of the script
timestamp = utils.getCurrentTimestampAsString()

# create the db tables if not existing
dbcontrol.readyDB()

# update the controller boot info
dbcontrol.updateControllerConfig(constants.CTRL_CONFIG_KEY_LAUNCHTIME, timestamp, timestamp)

# insert events into event table
dbcontrol.raiseEvent(timestamp, constants.EVENT_TYPE_CONTROLLER_STARTUP, constants.EVENT_PRIORITY_INFO, 'Poolsteuerung wurde gestartet.')
# log action for later statistics
dbcontrol.logAction(utils.getCurrentTimestampAsString(), constants.ACTION_TYPE_CONTROLLER_START, constants.ACTION_SOURCE_CONTROLLER, constants.ACTION_ENABLE)

emergencyMode = dbcontrol.getEmergencyMode()
if emergencyMode == constants.ON_STRING:
    gpioutils.activateEmergencyMode()

# check if in winter mode -> if yes then disable everything by setting winter gpio to ON and exit - other scripts won't run with this pin ON
automaticMode = dbcontrol.getAutomaticMode()
if automaticMode == constants.ON_STRING:
    gpioutils.activateAutomaticMode()

