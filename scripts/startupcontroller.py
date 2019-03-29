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

# wait until mysql and other mandatory deps started up
utils.waitSeconds(30)

# create the db tables if not existing
dbcontrol.readyDB()

# update the controller boot info
dbcontrol.updateControllerConfig(constants.CTRL_CONFIG_KEY_LAUNCHTIME, timestamp, timestamp)

# insert events into event table
dbcontrol.raiseEvent(timestamp, constants.EVENT_TYPE_CONTROLLER_STARTUP, constants.EVENT_PRIORITY_INFO, 'Poolsteuerung wurde gestartet.')

# check if in winter mode -> if yes then disable everything by setting winter gpio to ON and exit - other scripts won't run with this pin ON
wintermode = dbcontrol.getWinterMode()
if wintermode == constants.ON:
    # switch the winter mode gpio to ON
    gpioutils.activateWinterMode()
else:
    # summer mode, so lets go and enable the automatic mode pin
    gpioutils.activateAutomaticMode()

