import RPi.GPIO as GPIO

####################
# sensor constants #
####################

# battery status
SENSOR_BATTERY_STATUS_OK = 'OK'

# sensor IDs 
SENSOR_SOLAR_ID = 'SOLAR'
SENSOR_VORLAUF_ID = 'VORLAUF'
SENSOR_RUECKLAUF_ID = 'RUECKLAUF'
SENSOR_OUTDOOR_ID = 'OUTDOOR'
SENSOR_TECHNIK_ID = 'TECHNIK'
SENSOR_POOLWATER_ID = 'POOLWATER'
SENSOR_GREENHOUSE_ID = 'GREENHOUSE'
SENSOR_GARAGE_ID = 'GARAGE'
SENSOR_GARDENHOUSE_ID = 'GARDENHOUSE'

# 433 MHz temp sensors model
SENSOR_MODEL_VENICE = 'Ambient Weather F007TH Thermo-Hygrometer'

# 433 MHz temp sensors device id
SENSOR_POOLWATER = 11
SENSOR_OUTDOOR = 128
# not yet installed 433 MHz sensors
SENSOR_GREENHOUSE = ''
SENSOR_GARAGE = ''
SENSOR_GARDENHOUSE = ''
SENSOR_TECHNIK = ''

# 1wire sensor addresses
SENSOR_VORLAUF = '28-01143bba4eaa' # test sensor
SENSOR_RUECKLAUF = '28-01143bba4eaa' # test sensor
SENSOR_SOLAR = '28-01143bba4eaa' # test sensor

##################
# gpio constants #
##################

# PHYSISCH (mit verkabelung)
GPIO_PUMP = 19		# ansteuerung pumpenrelais
GPIO_SOLAR = 20		# ansteuerung ektr. kugelhahn solar

# LOGISCH  (ohne verkabelung)
GPIO_AUTOMATIC = 23	# automatic modus
GPIO_FILTER_MAN = 24	# manuelle pumpensteuerung
GPIO_SOLAR_MAN = 25	# manuelle elekt. kugelhahn solar steuerung
GPIO_WINTER_MODE = 26	# 0 = ON (Technik komplett aus) / 1 = OFF (Technik in Betrieb)

# on/off values
ON = GPIO.LOW
OFF = GPIO.HIGH
ON_STRING = 'ON'
OFF_STRING = 'OFF'

# sensor data keys and defaults

SENSOR_NO_DATA = -999;
SENSOR_ID_KEY = 'id'
SENSOR_TEMP_KEY = 't'
SENSOR_HUM_KEY = 'hum'
SENSOR_BAT_KEY = 'bat'
SENSOR_TIME_KEY = 'time'

# alert senders
ALERT_SENDER_DB = 'DBCONTROL'
ALERT_SENDER_POOLBOY = 'POOLBOY'

# alert keys
ALERT_SENDER_KEY = 'from'
ALERT_TIME_KEY = 'time'
ALERT_MSG_KEY = 'msg'

########
# MQTT #
########

MQTT_SERVER = 'localhost'

# topics
MQTT_TOPIC_ALERTS = '/home/extern/poolcontrol/alerts'
MQTT_TOPIC_TEMPS = '/home/extern/poolcontrol/sensors/temperatures'


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

############################
# controller configuration #
############################

# configuration keys
CTRL_CONFIG_KEY_LAUNCHTIME = 'CTRL-LAUNCHTIME'
CTRL_CONFIG_KEY_WINTERMODE = 'CTRL-WINTERMODE'
CTRL_CONFIG_KEY_FILTER_SCHEDULE_START = 'CTRL-FILTER-STARTTIME'
CTRL_CONFIG_KEY_FILTER_SCHEDULE_END = 'CTRL-FILTER-ENDTIME'
CTRL_CONFIG_KEY_SOLAR_DELTA = 'CTRL-SOLAR-DELTA'
CTRL_CONFIG_KEY_SOLAR_HYSTERESIS = 'CTRL-SOLAR-HYSTERESIS'
CTRL_CONFIG_KEY_FILTER_RUNTIME_MAX_DAILY = 'CTRL-FILTER-TIME-DAILY-MAX'
CTRL_CONFIG_KEY_FILTER_RUNTIME_DAILY = 'CTRL-FILTER-TIME-DAILY'
CTRL_CONFIG_KEY_FILTER_RUNTIME_OVERALL = 'CTRL-FILTER-TIME-OVERALL'

