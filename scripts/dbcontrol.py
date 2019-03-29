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

_GET_WINTER_MODE = """SELECT config_value FROM pc_configuration WHERE config_key='""" + constants.CTRL_CONFIG_KEY_WINTERMODE + """'"""


# load dbconfig from file
def loadDBConfig():
    with open('/home/pi/git/raspi-poolcontroller/scripts/dbconfig.json') as json_file:  
        return json.load(json_file)

# update controller startup info in DB
def updateControllerConfig(key, value, timestamp):
    with UseDatabase(dbconfig) as cursor:
        cursor.execute(_INSERT_OR_UPDATE_CONFIG, (key, value, timestamp, key, value, timestamp))

# issue some events written to DB
def raiseEvent(timestamp, event_type, prio, message):
    with UseDatabase(dbconfig) as cursor:
        cursor.execute(_RAISE_EVENT, (timestamp, event_type, prio, message))

# save sensor data to DB
def storeTemperature(sensor_id, timestamp, temp):
    with UseDatabase(dbconfig) as cursor:
        cursor.execute(_INSERT_SENSORDATA_TEMP, (sensor_id, timestamp, temp))

def storeClimate(sensor_id, timestamp, temp, humid, battery_status):
    with UseDatabase(dbconfig) as cursor:
        cursor.execute(_INSERT_SENSORDATA_CLIMATE, (sensor_id, timestamp, temp, humid, battery_status))

def activateWinterMode():
    updateControllerConfig(constants.CTRL_CONFIG_KEY_WINTERMODE, constants.ON_STRING, utils.getCurrentTimestampAsString())

def getWinterMode():
    with UseDatabase(dbconfig) as cursor:
        timestamp = utils.getCurrentTimestampAsString()
        cursor.execute(_GET_WINTER_MODE)
        data = cursor.fetchall()
        if len(data) == 1:
            mode = data[0][0].strip().upper()
            # we have a value stored in db - use it
            if mode == constants.ON_STRING:
                return constants.ON
            elif mode == constants.OFF_STRING:
                return constants.OFF
            else:
                # seems there is no valid value in the db - use fallback and raise a configuration error event
                raiseEvent(timestamp, constants.EVENT_TYPE_CONTROLLER_CONFIG, constants.EVENT_PRIORITY_ERROR, 'Fehlerhafter Konfigurationswert >' + mode + '< für den Wintermodus (' + constants.CTRL_CONFIG_KEY_WINTERMODE + '). Erlaubte Werte sind ' + constants.ON_STRING + ' / ' + constants.OFF_STRING + '. Bitte umgehend prüfen und ändern!')
                utils.sendAlert(constants.ALERT_SENDER_DB, 'Fehlerhafter Konfigurationswert: ' + constants.CTRL_CONFIG_KEY_WINTERMODE + '=' + mode + ' !')
                return constants.ON
        else:
            # seems there is no value in the db - use fallback and raise a configuration error event
            raiseEvent(timestamp, constants.EVENT_TYPE_CONTROLLER_CONFIG, constants.EVENT_PRIORITY_ERROR, 'Fehlender Konfigurationswert für den Wintermodus (' + constants.CTRL_CONFIG_KEY_WINTERMODE + '). Bitte umgehend korrigieren!')
            utils.sendAlert(constants.ALERT_SENDER_DB, 'Fehlender Konfigurationswert: ' + constants.CTRL_CONFIG_KEY_WINTERMODE + ' !')
            return constants.ON

# setup db table if required
def createTablesIfNeeded():
    with UseDatabase(dbconfig) as cursor:
        cursor.execute(_CREATE_CONFIG_TABLE)
        cursor.execute(_CREATE_EVENTS_TABLE)
        cursor.execute(_CREATE_SENSORDATA)

# prepare all database tables
def readyDB():
    # load db config
    dbconfig = loadDBConfig()
    createTablesIfNeeded()

dbconfig = loadDBConfig()

