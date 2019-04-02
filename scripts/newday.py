#############################################################################
# This script will reset the daily pump runtime counter and also update the #
# overall runtime counter and the launch date of the pump to midnight.      #
#############################################################################
import time

import constants # our own constants def file
import dbcontrol # our own db utils file
import gpioutils
import utils # our own utils file

# init gpio
gpioutils.init()

# remember call time
timestamp = utils.getCurrentTimestampAsString()

# reset the daily counter        
dbcontrol.updateControllerConfig(constants.CTRL_CONFIG_KEY_FILTER_RUNTIME_DAILY, 0, timestamp)

