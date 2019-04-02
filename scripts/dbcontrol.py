from datetime import datetime
import json
from DBcm import UseDatabase

import constants # our own constants def file
import utils # our own utils file

_CREATE_SENSORDATA = """CREATE TABLE IF NOT EXISTS pc_sensordata (
                sensor_id varchar(25) NOT NULL, 
                timestamp varchar(25) NOT NULL, 
                temperature decimal(5,2) NOT NULL,
                humidity decimal(5,2) NULL,
                battery varchar(20) NULL, 
                PRIMARY KEY(sensor_id, timestamp)
             )"""

_CREATE_CONFIG_TABLE = """CREATE TABLE IF NOT EXISTS pc_configuration (
                config_key varchar(50) PRIMARY KEY,
                config_value varchar(50) NOT NULL,  
                lastmodified varchar(25) NOT NULL
             )"""

_CREATE_EVENTS_TABLE = """CREATE TABLE IF NOT EXISTS pc_events (
                id INT AUTO_INCREMENT,
                timestamp varchar(25) NOT NULL,
                type varchar(20) NOT NULL,  
                prio varchar(10) NOT NULL,
                message varchar(255) NOT NULL,
                PRIMARY KEY(id)
             )"""

_CREATE_ACTIONS_TABLE = """CREATE TABLE IF NOT EXISTS pc_actions(id INT AUTO_INCREMENT,
                timestamp varchar(25) NOT NULL,
                actiontype varchar(20) NOT NULL,  
                actionsource varchar(20) NOT NULL,
                action varchar(255) NOT NULL,
                PRIMARY KEY(id)
             )"""

_INSERT_SENSORDATA_CLIMATE = """INSERT INTO pc_sensordata
                (sensor_id, timestamp, temperature, humidity, battery)
             VALUES
                (%s, %s, %s, %s, %s)"""

_INSERT_SENSORDATA_TEMP = """INSERT INTO pc_sensordata
                (sensor_id, timestamp, temperature)
             VALUES
                (%s, %s, %s)"""

_INSERT_OR_UPDATE_CONFIG = """INSERT INTO pc_configuration
                (config_key, config_value, lastmodified)
             VALUES
                (%s, %s, %s)
             ON DUPLICATE KEY UPDATE
                 config_key = %s, 
                 config_value = %s,
                 lastmodified = %s"""

_RAISE_EVENT = """INSERT INTO pc_events
                (timestamp, type, prio, message)
             VALUES
                (%s, %s, %s, %s)"""

_LOG_ACTION = """INSERT INTO pc_actions
                (timestamp, actiontype, actionsource, action)
             VALUES
                (%s, %s, %s, %s)"""

_GET_CONFIG_VALUE = """SELECT config_value FROM pc_configuration WHERE config_key='%DUMMY%'"""

_GET_LATEST_SENSOR_TEMP = """SELECT timestamp, temperature FROM pc_sensordata WHERE sensor_id='%DUMMY%' ORDER BY timestamp DESC LIMIT 1"""

# load dbconfig from file
def loadDBConfig():
    with open('/home/pi/git/poolboy/scripts/dbconfig.json') as json_file:  
        return json.load(json_file)

# update controller startup info in DB
def updateControllerConfig(key, value, timestamp):
    with UseDatabase(dbconfig) as cursor:
        cursor.execute(_INSERT_OR_UPDATE_CONFIG, (key, value, timestamp, key, value, timestamp))

# update controller startup info in DB
def queryControllerConfig(key, defaultValue):
    with UseDatabase(dbconfig) as cursor:
        timestamp = utils.getCurrentTimestampAsString()
        cursor.execute(_GET_CONFIG_VALUE.replace('%DUMMY%', key))
        data = cursor.fetchall()
        if len(data) == 1:
            value = data[0][0].strip().upper()
            if value != '':
                return value
            else:
                # seems there is no valid value in the db - use fallback and raise a configuration error event
                raiseEvent(timestamp, constants.EVENT_TYPE_CONTROLLER_CONFIG, constants.EVENT_PRIORITY_ERROR, 'Fehlerhafter Konfigurationswert >' + value + '< für ' + key + '. Bitte umgehend prüfen und ändern!')
                utils.sendAlert(constants.ALERT_SENDER_DB, 'Fehlerhafter Konfigurationswert: ' + key + '=' + value + ' !')
                return defaultValue
        else:
            # seems there is no value in the db - use fallback and raise a configuration error event
            raiseEvent(timestamp, constants.EVENT_TYPE_CONTROLLER_CONFIG, constants.EVENT_PRIORITY_ERROR, 'Fehlender Konfigurationswert für ' + key + '. Bitte umgehend korrigieren!')
            utils.sendAlert(constants.ALERT_SENDER_DB, 'Fehlender Konfigurationswert: ' + key + ' !')
            return defaultValue

# retrieve the latest temperature a sensor has reported
def getLastestSensorTemperature(sensor):
    sensorDataExpireInMinutes = queryControllerConfig(constants.CTRL_CONFIG_KEY_SENSOR_MAX_AGE_IN_MINUTES, constants.CTRL_CONFIG_DEFAULT_SENSOR_MAX_AGE_IN_MINUTES)
    with UseDatabase(dbconfig) as cursor:
        cursor.execute(_GET_LATEST_SENSOR_TEMP.replace('%DUMMY%', sensor))
        data = cursor.fetchall()
        if len(data) == 1:
            timestamp = data[0][0].strip()
            value = data[0][1]

            #  do not deliver sensor data older than SENSOR_MAX_AGE_IN_MINUTES
            if utils.calculateDurationInMinutes(utils.getCurrentTimestampAsString(), timestamp) > int(sensorDataExpireInMinutes):
                return constants.SENSOR_NO_DATA

            if value != '':
                return float(value)
            else:
                return constants.SENSOR_NO_DATA
        else:
            return constants.SENSOR_NO_DATA

# issue some events written to DB
def raiseEvent(timestamp, event_type, prio, message):
    with UseDatabase(dbconfig) as cursor:
        cursor.execute(_RAISE_EVENT, (timestamp, event_type, prio, message))

# log an action for statistics
def logAction(timestamp, actionType, actionSource, action):
    with UseDatabase(dbconfig) as cursor:
        cursor.execute(_LOG_ACTION, (timestamp, actionType, actionSource, action))

# save sensor data to DB
def storeTemperature(sensor_id, timestamp, temp):
    with UseDatabase(dbconfig) as cursor:
        cursor.execute(_INSERT_SENSORDATA_TEMP, (sensor_id, timestamp, temp))

def storeClimate(sensor_id, timestamp, temp, humid, battery_status):
    with UseDatabase(dbconfig) as cursor:
        cursor.execute(_INSERT_SENSORDATA_CLIMATE, (sensor_id, timestamp, temp, humid, battery_status))

def activateFrostMode():
    updateControllerConfig(constants.CTRL_CONFIG_KEY_FROSTMODE, constants.ON_STRING, utils.getCurrentTimestampAsString())

def updateAutomaticMode(status):
    if status == True or status == constants.ON or status == constants.ON_STRING:
        status = constants.ON_STRING
    else:
        status = constants.OFF_STRING
    updateControllerConfig(constants.CTRL_CONFIG_KEY_AUTOMATIC, status, utils.getCurrentTimestampAsString())

def updateEmergencyMode(status):
    if status == True or status == constants.ON or status == constants.ON_STRING:
        status = constants.ON_STRING
    else:
        status = constants.OFF_STRING
    updateControllerConfig(constants.CTRL_CONFIG_KEY_EMERGENCY, status, utils.getCurrentTimestampAsString())

def setSolarLaunchTime(timestamp):
    updateControllerConfig(constants.CTRL_CONFIG_KEY_SOLAR_ENABLE_TIME, timestamp, timestamp)

def updateSolarRuntime():
    # remember call time
    timestamp = utils.getCurrentTimestampAsString()

    # obtain the last launch time and the overall solar runtime from db
    solarLaunched = getSolarLaunchTime()

    # obtain the overall solar runtime
    overall = int(queryControllerConfig(constants.CTRL_CONFIG_KEY_SOLAR_RUNTIME, constants.CTRL_CONFIG_DEFAULT_SOLAR_RUNTIME))

    if solarLaunched == '':
        # something went wrong...we should have had a value for the last solar launch
        utils.sendAlert(constants.ALERT_SENDER_DB, "Warnung! Der Startzeitpunkt des Solarabsorbers konnte nicht ermittelt werden. Keine Laufzeitprotokollierung.")
    else:
        # calculate the runtime duration in minutes
        overall = overall + utils.calculateDurationInMinutes(timestamp, solarLaunched)
        # save the overall runtime to db
        updateControllerConfig(constants.CTRL_CONFIG_KEY_SOLAR_RUNTIME, overall, timestamp)

    # reset the last lauch time in db
    updateControllerConfig(constants.CTRL_CONFIG_KEY_SOLAR_ENABLE_TIME, '', timestamp)

def setPumpLaunchTime(timestamp):
    updateControllerConfig(constants.CTRL_CONFIG_KEY_FILTER_ENABLE_TIME, timestamp, timestamp)

def updatePumpRuntime():
    # remember call time
    timestamp = utils.getCurrentTimestampAsString()

    # obtain the last launch time and the overall pump runtime from db
    pumpLaunched = getPumpLaunchTime()

    # obtain the overall and daily pump runtime
    overall = int(queryControllerConfig(constants.CTRL_CONFIG_KEY_FILTER_RUNTIME_OVERALL, constants.CTRL_CONFIG_DEFAULT_FILTER_RUNTIME))
    daily   = int(queryControllerConfig(constants.CTRL_CONFIG_KEY_FILTER_RUNTIME_DAILY, constants.CTRL_CONFIG_DEFAULT_FILTER_RUNTIME))

    if pumpLaunched == '':
        # something went wrong...we should have had a value for the last pump launch
        utils.sendAlert(constants.ALERT_SENDER_DB, "Warnung! Der Startzeitpunkt der Filterpumpe konnte nicht ermittelt werden. Keine Laufzeitprotokollierung.")
    else:
        # calculate the runtime duration in minutes
        durationInMinutes = utils.calculateDurationInMinutes(timestamp, pumpLaunched)
        overall = overall + durationInMinutes
        midnight = datetime.now().replace(hour=0, minute=0, second=0)
        # for the daily counter we only count time take on the same day
        if datetime.strptime(pumpLaunched, '%Y-%m-%d %H:%M:%S') < midnight:
            durationInMinutes = utils.calculateDurationInMinutes(timestamp, midnight)
        daily = daily + durationInMinutes
        # save the overall and daily runtimes to db
        updateControllerConfig(constants.CTRL_CONFIG_KEY_FILTER_RUNTIME_OVERALL, overall, timestamp)
        updateControllerConfig(constants.CTRL_CONFIG_KEY_FILTER_RUNTIME_DAILY, daily, timestamp)

    # reset the last lauch time in db
    updateControllerConfig(constants.CTRL_CONFIG_KEY_FILTER_ENABLE_TIME, '', timestamp)

def getEmergencyMode():
    return queryControllerConfig(constants.CTRL_CONFIG_KEY_EMERGENCY, constants.ON)

def getAutomaticMode():
    return queryControllerConfig(constants.CTRL_CONFIG_KEY_AUTOMATIC, constants.OFF)

def getFrostMode():
    return queryControllerConfig(constants.CTRL_CONFIG_KEY_FROSTMODE, constants.ON)

def getFrostModeActivationLimit():
    return queryControllerConfig(constants.CTRL_CONFIG_KEY_FROSTMODE_LIMIT, constants.CTRL_CONFIG_DEFAULT_FROSTMODE_LIMIT)

def getHeatingOverrideMode():
    return queryControllerConfig(constants.CTRL_CONFIG_KEY_HEATING_OVERRIDE, constants.ON)

def getMinimalSolarRuntime():
    return queryControllerConfig(constants.CTRL_CONFIG_KEY_SOLAR_MIN_RUNTIME, constants.CTRL_CONFIG_DEFAULT_SOLAR_MIN_RUNTIME)

def getScheduledFilterStartTime():
    return queryControllerConfig(constants.CTRL_CONFIG_KEY_FILTER_SCHEDULE_START, constants.CTRL_CONFIG_DEFAULT_FILTER_SCHEDULE_START)

def getScheduledFilterStopTime():
    return queryControllerConfig(constants.CTRL_CONFIG_KEY_FILTER_SCHEDULE_STOP, constants.CTRL_CONFIG_DEFAULT_FILTER_SCHEDULE_STOP)

def getMaxDailyFilterTimeInMinutes():
    return int(queryControllerConfig(constants.CTRL_CONFIG_KEY_FILTER_RUNTIME_MAX_DAILY, constants.CTRL_CONFIG_DEFAULT_FILTER_RUNTIME_MAX_DAILY))

def getSolarEnableDelta():
    return int(queryControllerConfig(constants.CTRL_CONFIG_KEY_SOLAR_ENABLE_DELTA, constants.CTRL_CONFIG_DEFAULT_SOLAR_ENABLE_DELTA))

def getSolarDisableDelta():
    return int(queryControllerConfig(constants.CTRL_CONFIG_KEY_SOLAR_DISABLE_DELTA, constants.CTRL_CONFIG_DEFAULT_SOLAR_DISABLE_DELTA))

def getPumpDailyRuntime():
    return int(queryControllerConfig(constants.CTRL_CONFIG_KEY_FILTER_RUNTIME_DAILY, constants.CTRL_CONFIG_DEFAULT_FILTER_RUNTIME))

def getPumpDailyRuntimeMax():
    return int(queryControllerConfig(constants.CTRL_CONFIG_KEY_FILTER_RUNTIME_MAX_DAILY, constants.CTRL_CONFIG_DEFAULT_FILTER_RUNTIME_MAX_DAILY))

def getPumpLaunchTime():
    return queryControllerConfig(constants.CTRL_CONFIG_KEY_FILTER_ENABLE_TIME, '')

def getSolarLaunchTime():
    return queryControllerConfig(constants.CTRL_CONFIG_KEY_SOLAR_ENABLE_TIME, '')

def getMaximumPoolTemperature():
    return queryControllerConfig(constants.CTRL_CONFIG_KEY_MAX_POOL_TEMP, constants.CTRL_CONFIG_DEFAULT_MAX_POOL_TEMP)

# setup db table if required
def createTablesIfNeeded():
    with UseDatabase(dbconfig) as cursor:
        cursor.execute(_CREATE_CONFIG_TABLE)
        cursor.execute(_CREATE_EVENTS_TABLE)
        cursor.execute(_CREATE_SENSORDATA)
        cursor.execute(_CREATE_ACTIONS_TABLE)

# prepare all database tables
def readyDB():
    # load db config
    dbconfig = loadDBConfig()
    createTablesIfNeeded()

dbconfig = loadDBConfig()

