# create database
create database poolcontrol;

# grant privileges on database
grant all privileges on poolcontrol.* to 'poolboy'@'localhost' identified by '<passwort>'

# tables are created automatically at runtime

# useful configuration defaults
insert into pc_configuration (config_key, config_value) values ('FROST-MODE', 'OFF'); # frost secure mode / works only in automatic mode
insert into pc_configuration (config_key, config_value) values ('FROSTMODE-LIMIT', '2'); # frost mode limit
insert into pc_configuration (config_key, config_value) values ('EMERGENCY-MODE', 'OFF'); # emergency mode triggered when there is a problem with the pool
insert into pc_configuration (config_key, config_value) values ('HEATING-OVERRIDE', 'ON'); # only in automatic mode - if solar has enough heat we can heat also outside the filter schedule
insert into pc_configuration (config_key, config_value) values ('SOLAR-ENABLE-DELTA', '5'); # temperature delta for activating solar
insert into pc_configuration (config_key, config_value) values ('SOLAR-DISABLE-DELTA', '2'); # temperature delta for deactivating solar
insert into pc_configuration (config_key, config_value) values ('SENSORDATA-MAX-AGE', '15'); # maximum age in minutes of a measured temperature value to be considered for calculations
insert into pc_configuration (config_key, config_value) values ('SOLAR-MIN-RUNTIME', '5'); # minimum runtime of the solar mode to be able to deactivate again
insert into pc_configuration (config_key, config_value) values ('MAXIMUM-POOL-TEMP', '30'); # max pool temp
insert into pc_configuration (config_key, config_value) values ('COOLER-ENABLE-DELTA', '2'); # temperature delta for activating cooler mode to cool down pool temperature if too high
insert into pc_configuration (config_key, config_value) values ('TEMPERATURE-UNIT', 'C'); # how to display temps (C=Celsius, F=Fahrenheit)


# some sensors
# 1wire
insert into pc_sensors (sensor_location_id, sensor_transmit_type, sensor_model, sensor_channel, sensor_address, temperatureunit) values ('SOLAR', '1WIRE', '', '', '28-00000b1fd98a', 'C');
insert into pc_sensors (sensor_location_id, sensor_transmit_type, sensor_model, sensor_channel, sensor_address, temperatureunit) values ('FROM-POOL', '1WIRE', '', '', '28-01143bba4eaa', 'C');
insert into pc_sensors (sensor_location_id, sensor_transmit_type, sensor_model, sensor_channel, sensor_address, temperatureunit) values ('TO-POOL', '1WIRE', '', '', '28-01143d2d03aa', 'C');

# 433MHz radio
insert into pc_sensors (sensor_location_id, sensor_transmit_type, sensor_model, sensor_channel, sensor_address, temperatureunit) values ('POOLWATER', '433MHZ', 'Ambient Weather F007TH Thermo-Hygrometer', '1', '', 'F');
insert into pc_sensors (sensor_location_id, sensor_transmit_type, sensor_model, sensor_channel, sensor_address, temperatureunit) values ('OUTDOOR', '433MHZ', 'Ambient Weather F007TH Thermo-Hygrometer', '2', '', 'F');


# some filter times
insert into pc_filterschedule (filterstart, filterstop) values ('06:00', '08:00');
insert into pc_filterschedule (filterstart, filterstop) values ('11:00', '13:00');
insert into pc_filterschedule (filterstart, filterstop) values ('16:00', '18:00');

