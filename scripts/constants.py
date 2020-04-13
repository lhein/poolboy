import RPi.GPIO as GPIO

POOLBOY_INSTALL_FOLDER = '/home/pi/git/poolboy'

####################
# sensor constants #
####################

# battery status
SENSOR_BATTERY_STATUS_OK = 'OK'

# temperature units
TEMP_CELSIUS = 'C'
TEMP_FAHRENHEIT = 'F'

# sensor types
SENSOR_TYPE_433MHZ = '433MHZ'
SENSOR_TYPE_1WIRE  = '1WIRE'

# sensor IDs 
SENSOR_SOLAR_ID = 'SOLAR'
SENSOR_VORLAUF_ID = 'FROM-POOL'
SENSOR_RUECKLAUF_ID = 'TO-POOL'
SENSOR_OUTDOOR_ID = 'OUTDOOR'
SENSOR_TECHNIK_ID = 'POOLHOUSE'
SENSOR_POOLWATER_ID = 'POOLWATER'
SENSOR_GREENHOUSE_ID = 'GREENHOUSE'
SENSOR_GARAGE_ID = 'GARAGE'
SENSOR_GARDENHOUSE_ID = 'GARDENHOUSE'


##################
# gpio constants #
##################

# PHYSISCH (mit verkabelung)
GPIO_PUMP = 19		# ansteuerung pumpenrelais
GPIO_SOLAR = 20	# ansteuerung ektr. kugelhahn solar

# LOGISCH  (ohne verkabelung)
GPIO_EMERGENCY_MODE = 21 # Not-Aus
GPIO_COOLER_MODE = 22   # Kuehlung 
GPIO_AUTOMATIC = 23	# automatic modus
GPIO_FILTER_MAN = 24	# manuelle pumpensteuerung
GPIO_SOLAR_MAN = 25	# manuelle elekt. kugelhahn solar steuerung
GPIO_FROST_MODE = 26	# 0 = ON (Pumpe und Solar an) / 1 = OFF (keine Pumpe und kein Solar)
GPIO_SOLAR_OPENED = 5   # 0 = YES (Solar-Circuit is open / 1 = NO (Solar absorbers are not used)
GPIO_SOLAR_CLOSED = 6   # 0 = YES (Solar-Circuit is closed / 1 = NO (Solar absorbers are used)

# on/off values
ON = GPIO.LOW
OFF = GPIO.HIGH
#ON = GPIO.HIGH
#OFF = GPIO.LOW
ON_STRING = 'ON'
OFF_STRING = 'OFF'

# sensor data keys and defaults
SENSOR_NO_DATA = -999.0

###################
# event constants #
###################

# event types
EVENT_TYPE_CONTROLLER_STARTUP = 'CTRL-STARTUP'
EVENT_TYPE_CONTROLLER_MODE = 'CTRL-MODE'
EVENT_TYPE_CONTROLLER_CONFIG = 'CTRL-CONFIG'
EVENT_TYPE_DEVICE_STATE = 'DEVICE-STATE'

# event priorities
EVENT_PRIORITY_INFO = 'INFO'
EVENT_PRIORITY_WARNING = 'WARNING'
EVENT_PRIORITY_ERROR = 'ERROR'


####################
# action constants #
####################

# action types
ACTION_TYPE_CONTROLLER_START = 'CONTROLLER START'
ACTION_TYPE_MODE_SWITCH = 'MODE CHANGE'
ACTION_TYPE_HW_STATUS = 'HARDWARE STATUS'

# action sources
ACTION_SOURCE_MODE_AUTOMATIC = 'AUTOMATIC'
ACTION_SOURCE_MODE_EMERGENCY = 'EMERGENCY'
ACTION_SOURCE_MODE_FROST = 'FROST'
ACTION_SOURCE_MODE_COOLER = 'COOLER'
ACTION_SOURCE_MODE_EMERGENCY = 'EMERGENCY'
ACTION_SOURCE_MODE_MANUALFILTER = 'MANUAL FILTER MODE'
ACTION_SOURCE_MODE_MANUALSOLAR = 'MANUAL SOLAR MODE'
ACTION_SOURCE_MODE_SOLAROVERRIDE = 'SOLAR OVERRIDE MODE'
ACTION_SOURCE_CONTROLLER = 'CONTROLLER'
ACTION_SOURCE_PUMP = 'PUMP'
ACTION_SOURCE_SOLAR = 'SOLAR'

# actions
ACTION_ENABLE = ON_STRING
ACTION_DISABLE = OFF_STRING


############################
# controller configuration #
############################

# configuration keys
CTRL_CONFIG_KEY_LAUNCHTIME = 'CTRL-LAUNCHTIME'
CTRL_CONFIG_KEY_AUTOMATIC = 'AUTOMATIC-MODE'
CTRL_CONFIG_KEY_FROSTMODE = 'FROST-MODE'
CTRL_CONFIG_KEY_FROSTMODE_LIMIT = 'FROSTMODE-LIMIT'
CTRL_CONFIG_KEY_EMERGENCY = 'EMERGENCY-MODE'
CTRL_CONFIG_KEY_FILTER_OVERRIDE = 'FILTER-OVERRIDE'
CTRL_CONFIG_KEY_SOLAR_ENABLE_DELTA = 'SOLAR-ENABLE-DELTA'
CTRL_CONFIG_KEY_SOLAR_DISABLE_DELTA = 'SOLAR-DISABLE-DELTA'
CTRL_CONFIG_KEY_SOLAR_MIN_RUNTIME = 'SOLAR-MIN-RUNTIME'
CTRL_CONFIG_KEY_FILTER_RUNTIME_OVERALL = 'PUMP-RUNTIME-OVERALL'
CTRL_CONFIG_KEY_FILTER_ENABLE_TIME = 'PUMP-LAUNCHTIME'
CTRL_CONFIG_KEY_SOLAR_ENABLE_TIME = 'SOLAR-LAUNCHTIME'
CTRL_CONFIG_KEY_SOLAR_RUNTIME = 'SOLAR-RUNTIME'
CTRL_CONFIG_KEY_SENSOR_MAX_AGE_IN_MINUTES = 'SENSORDATA-MAX-AGE'
CTRL_CONFIG_KEY_MAX_POOL_TEMP = 'MAXIMUM-POOL-TEMP'
CTRL_CONFIG_KEY_COOLER_ENABLE_DELTA = 'COOLER-ENABLE-DELTA'
CTRL_CONFIG_KEY_TEMPERATURE_UNIT = 'TEMPERATURE-UNIT'

# default fallback values
CTRL_CONFIG_DEFAULT_SOLAR_ENABLE_DELTA = 5
CTRL_CONFIG_DEFAULT_SOLAR_DISABLE_DELTA = 2
CTRL_CONFIG_DEFAULT_SOLAR_RUNTIME = 0
CTRL_CONFIG_DEFAULT_FILTER_RUNTIME = 0
CTRL_CONFIG_DEFAULT_SENSOR_MAX_AGE_IN_MINUTES = 15
CTRL_CONFIG_DEFAULT_FROSTMODE_LIMIT = 2
CTRL_CONFIG_DEFAULT_SOLAR_MIN_RUNTIME = 5
CTRL_CONFIG_DEFAULT_MAX_POOL_TEMP = 30
CTRL_CONFIG_DEFAULT_COOLER_ENABLE_DELTA = 2
CTRL_CONFIG_DEFAULT_TEMPERATURE_UNIT = TEMP_CELSIUS

