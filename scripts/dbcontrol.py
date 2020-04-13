from datetime import datetime
import json
from DBcm import UseDatabase

import commons
import constants # our own constants def file
import utils # our own utils file

from sensor import Sensor
from filterschedule import FilterSchedule


_CREATE_SENSORDATA_TABLE = """CREATE TABLE IF NOT EXISTS pc_sensordata (
                sensor_id varchar(25) NOT NULL, 
                timestamp varchar(25) NOT NULL, 
                temperature decimal(5,2) NOT NULL,
                temperatureunit varchar(1) NOT NULL,
                humidity decimal(5,2) NULL,
                battery varchar(20) NULL, 
                PRIMARY KEY(sensor_id, timestamp)
             )"""

_CREATE_SENSORS_TABLE = """CREATE TABLE IF NOT EXISTS pc_sensors (
                id INT AUTO_INCREMENT,
                sensor_location_id varchar(25) NOT NULL, 
                sensor_transmit_type varchar(20) NOT NULL,
                sensor_model varchar(200),
                sensor_channel varchar(10),
                sensor_address varchar(20),
                temperatureunit varchar(1) NOT NULL,
                lastmodified varchar(25) NOT NULL, 
                PRIMARY KEY(id)
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

_CREATE_FILTER_SCHEDULE_TABLE = """CREATE TABLE IF NOT EXISTS pc_filterschedule(
                id INT AUTO_INCREMENT,
                filterstart varchar(5) NOT NULL,
                filterstop  varchar(5) NOT NULL,  
                lastmodified varchar(25) NOT NULL,
                PRIMARY KEY(id)
             )"""

_INSERT_SENSORDATA_CLIMATE = """INSERT INTO pc_sensordata
                (sensor_id, timestamp, temperature, temperatureunit, humidity, battery)
             VALUES
                (%s, %s, %s, %s, %s, %s)"""

_INSERT_SENSORDATA_TEMP = """INSERT INTO pc_sensordata
                (sensor_id, timestamp, temperature, temperatureunit)
             VALUES
                (%s, %s, %s, %s)"""

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

_GET_FILTER_SCHEDULES = """SELECT filterstart, filterstop FROM pc_filterschedule ORDER BY filterstart"""

_GET_SENSORS = """SELECT sensor_location_id, sensor_transmit_type, sensor_model, sensor_channel, sensor_address, temperatureunit FROM pc_sensors WHERE sensor_transmit_type='%DUMMY%'"""

_GET_CONFIG_VALUE = """SELECT config_value FROM pc_configuration WHERE config_key='%DUMMY%'"""

_GET_LATEST_SENSOR_TEMP = """SELECT timestamp, temperature, temperatureunit FROM pc_sensordata WHERE sensor_id='%DUMMY%' ORDER BY timestamp DESC LIMIT 1"""

# load dbconfig from file
def loadDBConfig():
    with open(constants.POOLBOY_INSTALL_FOLDER + '/scripts/dbconfig.json') as json_file:  
        return json.load(json_file)

# update controller startup info in DB
def updateControllerConfig(key, value, timestamp):
    with UseDatabase(dbconfig) as cursor:
        cursor.execute(_INSERT_OR_UPDATE_CONFIG, (key, value, timestamp, key, value, timestamp))

# update controller startup info in DB
def queryControllerConfig(key, defaultValue):
    with UseDatabase(dbconfig) as cursor:
        timestamp = commons.getCurrentTimestampAsString()
        cursor.execute(_GET_CONFIG_VALUE.replace('%DUMMY%', key))
        data = cursor.fetchall()
        if len(data) == 1:
            value = data[0][0].strip().upper()
            if value != '':
                return value
            else:
                # seems there is no valid value in the db - use fallback and raise a configuration error event
                raiseEvent(timestamp, constants.EVENT_TYPE_CONTROLLER_CONFIG, constants.EVENT_PRIORITY_ERROR, 'Invalid configuration value >' + value + '< for ' + key + '. Please check the value and correct it!')
                return defaultValue
        else:
            # seems there is no value in the db - use fallback and raise a configuration error event
            raiseEvent(timestamp, constants.EVENT_TYPE_CONTROLLER_CONFIG, constants.EVENT_PRIORITY_ERROR, 'Missing configuration value for ' + key + '. Please fix this asap!')
            return defaultValue

def getSystemTemperatureUnit():
    return queryControllerConfig(constants.CTRL_CONFIG_KEY_TEMPERATURE_UNIT, constants.CTRL_CONFIG_DEFAULT_TEMPERATURE_UNIT)

# retrieve the latest temperature a sensor has reported
def getLastestSensorTemperature(sensor):
    sensorDataExpireInMinutes = queryControllerConfig(constants.CTRL_CONFIG_KEY_SENSOR_MAX_AGE_IN_MINUTES, constants.CTRL_CONFIG_DEFAULT_SENSOR_MAX_AGE_IN_MINUTES)
    with UseDatabase(dbconfig) as cursor:
        cursor.execute(_GET_LATEST_SENSOR_TEMP.replace('%DUMMY%', sensor))
        data = cursor.fetchall()
        if len(data) == 1:
            timestamp = data[0][0].strip()
            value = data[0][1]
            unit = data[0][2]

            #  do not deliver sensor data older than SENSOR_MAX_AGE_IN_MINUTES
            if commons.calculateDurationInMinutes(commons.getCurrentTimestampAsString(), timestamp) > int(sensorDataExpireInMinutes):
                raiseEvent(timestamp, constants.EVENT_TYPE_DEVICE_STATE, constants.EVENT_PRIORITY_WARNING, 'Outdated temperature information for sensor ' + sensor + '! Last measured value is from ' + timestamp + '. Please check the sensor!')
                return constants.SENSOR_NO_DATA

            if value != '':
                sysUnit = getSystemTemperatureUnit()
                if unit != sysUnit:
                    value = commons.convertTemperatureTo(value, sysUnit)
                return float(value)
            else:
                return constants.SENSOR_NO_DATA
        else:
            return constants.SENSOR_NO_DATA

# issue some events written to DB
def raiseEvent(timestamp, event_type, prio, message):
    with UseDatabase(dbconfig) as cursor:
        cursor.execute(_RAISE_EVENT, (timestamp, event_type, prio, message))

# retrieve all configured sensors
def getSensorsForType(sensorType):
    sensors = []

    with UseDatabase(dbconfig) as cursor:
        cursor.execute(_GET_SENSORS.replace('%DUMMY%', sensorType))
        data = cursor.fetchall()
        if len(data) > 0:
            for row in data:
                sensors.append(Sensor(row[0], row[1], row[2], row[3], row[4], row[5]))

    return sensors

# retrieve the filter schedule times
def getFilterSchedules():
    schedules = []

    with UseDatabase(dbconfig) as cursor:
        cursor.execute(_GET_FILTER_SCHEDULES)
        data = cursor.fetchall()
        if len(data) > 0:
            for row in data:
                schedules.append(FilterSchedule(row[0], row[1]))
        else:
            timestamp = commons.getCurrentTimestampAsString()
            raiseEvent(timestamp, constants.EVENT_TYPE_CONTROLLER_CONFIG, constants.EVENT_PRIORITY_ERROR, 'There are filter times scheduled!')
            updateAutomaticMode(False)

    return schedules

# log an action for statistics
def logAction(timestamp, actionType, actionSource, action):
    with UseDatabase(dbconfig) as cursor:
        cursor.execute(_LOG_ACTION, (timestamp, actionType, actionSource, action))

# save sensor data to DB
def storeTemperature(sensor_id, timestamp, temp, unit):
    with UseDatabase(dbconfig) as cursor:
        cursor.execute(_INSERT_SENSORDATA_TEMP, (sensor_id, timestamp, temp, unit))

def storeClimate(sensor_id, timestamp, temp, unit, humid, battery_status):
    with UseDatabase(dbconfig) as cursor:
        cursor.execute(_INSERT_SENSORDATA_CLIMATE, (sensor_id, timestamp, temp, unit, humid, battery_status))

def activateFrostMode():
    updateControllerConfig(constants.CTRL_CONFIG_KEY_FROSTMODE, constants.ON_STRING, commons.getCurrentTimestampAsString())

def updateAutomaticMode(status):
    if status == True or status == constants.ON or status == constants.ON_STRING:
        status = constants.ON_STRING
    else:
        status = constants.OFF_STRING
    updateControllerConfig(constants.CTRL_CONFIG_KEY_AUTOMATIC, status, commons.getCurrentTimestampAsString())

def updateEmergencyMode(status):
    if status == True or status == constants.ON or status == constants.ON_STRING:
        status = constants.ON_STRING
    else:
        status = constants.OFF_STRING
    updateControllerConfig(constants.CTRL_CONFIG_KEY_EMERGENCY, status, commons.getCurrentTimestampAsString())

def setSolarLaunchTime(timestamp):
    updateControllerConfig(constants.CTRL_CONFIG_KEY_SOLAR_ENABLE_TIME, timestamp, timestamp)

def updateSolarRuntime():
    # remember call time
    timestamp = commons.getCurrentTimestampAsString()

    # obtain the last launch time and the overall solar runtime from db
    solarLaunched = getSolarLaunchTime()

    # obtain the overall solar runtime
    overall = int(queryControllerConfig(constants.CTRL_CONFIG_KEY_SOLAR_RUNTIME, constants.CTRL_CONFIG_DEFAULT_SOLAR_RUNTIME))

    if solarLaunched == '':
        # something went wrong...we should have had a value for the last solar launch
        raiseEvent(timestamp, constants.EVENT_TYPE_CONTROLLER_CONFIG, constants.EVENT_PRIORITY_WARNING, 'Warning! Unable to determine the start time of the solar absorber. Cannot log the runtime.')
    else:
        # calculate the runtime duration in minutes
        overall = overall + commons.calculateDurationInMinutes(timestamp, solarLaunched)
        # save the overall runtime to db
        updateControllerConfig(constants.CTRL_CONFIG_KEY_SOLAR_RUNTIME, overall, timestamp)

    # reset the last lauch time in db
    updateControllerConfig(constants.CTRL_CONFIG_KEY_SOLAR_ENABLE_TIME, '', timestamp)

def setPumpLaunchTime(timestamp):
    updateControllerConfig(constants.CTRL_CONFIG_KEY_FILTER_ENABLE_TIME, timestamp, timestamp)

def updatePumpRuntime():
    # remember call time
    timestamp = commons.getCurrentTimestampAsString()

    # obtain the last launch time and the overall pump runtime from db
    pumpLaunched = getPumpLaunchTime()

    # obtain the overall and daily pump runtime
    overall = int(queryControllerConfig(constants.CTRL_CONFIG_KEY_FILTER_RUNTIME_OVERALL, constants.CTRL_CONFIG_DEFAULT_FILTER_RUNTIME))

    if pumpLaunched == '':
        # something went wrong...we should have had a value for the last pump launch
        raiseEvent(timestamp, constants.EVENT_TYPE_CONTROLLER_CONFIG, constants.EVENT_PRIORITY_WARNING, 'Warning! Unable to determine the start time of the filter pump. Cannot log the runtime.')
    else:
        # calculate the runtime duration in minutes
        durationInMinutes = commons.calculateDurationInMinutes(timestamp, pumpLaunched)
        overall = overall + durationInMinutes
        # save the overall runtime to db
        updateControllerConfig(constants.CTRL_CONFIG_KEY_FILTER_RUNTIME_OVERALL, overall, timestamp)

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

def getFilterOverrideMode():
    return queryControllerConfig(constants.CTRL_CONFIG_KEY_FILTER_OVERRIDE, constants.ON)

def getMinimalSolarRuntime():
    return queryControllerConfig(constants.CTRL_CONFIG_KEY_SOLAR_MIN_RUNTIME, constants.CTRL_CONFIG_DEFAULT_SOLAR_MIN_RUNTIME)

def getSolarEnableDelta():
    return int(queryControllerConfig(constants.CTRL_CONFIG_KEY_SOLAR_ENABLE_DELTA, constants.CTRL_CONFIG_DEFAULT_SOLAR_ENABLE_DELTA))

def getSolarDisableDelta():
    return int(queryControllerConfig(constants.CTRL_CONFIG_KEY_SOLAR_DISABLE_DELTA, constants.CTRL_CONFIG_DEFAULT_SOLAR_DISABLE_DELTA))

def getPumpLaunchTime():
    return queryControllerConfig(constants.CTRL_CONFIG_KEY_FILTER_ENABLE_TIME, '')

def getSolarLaunchTime():
    return queryControllerConfig(constants.CTRL_CONFIG_KEY_SOLAR_ENABLE_TIME, '')

def getMaximumPoolTemperature():
    return queryControllerConfig(constants.CTRL_CONFIG_KEY_MAX_POOL_TEMP, constants.CTRL_CONFIG_DEFAULT_MAX_POOL_TEMP)

def getCoolerEnableDelta():
    return int(queryControllerConfig(constants.CTRL_CONFIG_KEY_COOLER_ENABLE_DELTA, constants.CTRL_CONFIG_DEFAULT_COOLER_ENABLE_DELTA))

# setup db table if required
def createTablesIfNeeded():
    with UseDatabase(dbconfig) as cursor:
        cursor.execute(_CREATE_CONFIG_TABLE)
        cursor.execute(_CREATE_EVENTS_TABLE)
        cursor.execute(_CREATE_SENSORDATA_TABLE)
        cursor.execute(_CREATE_ACTIONS_TABLE)
        cursor.execute(_CREATE_FILTER_SCHEDULE_TABLE)
        cursor.execute(_CREATE_SENSORS_TABLE)

# prepare all database tables
def readyDB():
    # load db config
    dbconfig = loadDBConfig()
    createTablesIfNeeded()

dbconfig = loadDBConfig()

