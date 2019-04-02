# DB erstellen
create database poolcontrol;
grant all privileges on poolcontrol.* to 'poolboy'@'localhost' identified by '<passwort>'

# Tabellen erstellen
# die Tabellen werden automatisch erstellt

# useful defaults füllen (nachdem die Tabellen erstellt wurden)
insert into pc_configuration (config_key, config_value) values ('FROSTMODE', 'OFF'); # Frostschutzmodus
insert into pc_configuration (config_key, config_value) values ('EMERGENCY-MODE', 'OFF'); # Notfallmodus bei Fehler in der Anlage
insert into pc_configuration (config_key, config_value) values ('PUMP-DAILY-RUN', '360'); # Laufzeit der Pumpe pro Tag in Minuten
insert into pc_configuration (config_key, config_value) values ('HEATING-OVERRIDE', 'ON'); # Bei möglichem Solarerstrag die Pumpe aktivieren? (nur im Automatikmodus)
insert into pc_configuration (config_key, config_value) values ('SOLAR-ENABLE-DELTA', '5'); # Temperatur Delta zw. Solar und Vorlauf in Grad bei der Solar aktiviert wird im Automatikbetrieb
insert into pc_configuration (config_key, config_value) values ('SOLAR-DISABLE-DELTA', '2'); # Temperatur Delta zw. Rücklauf und Vorlauf in Grad bei der Solar deaktiviert wird im Automatikbetrieb
insert into pc_configuration (config_key, config_value) values ('PUMP-SCHEDULE-START', '08:00'); # die startzeit des tägl. Filterzeitfensters
insert into pc_configuration (config_key, config_value) values ('PUMP-SCHEDULE-STOP', '19:00'); # die endzeit des tägl. Filterzeitfensters
insert into pc_configuration (config_key, config_value) values ('SENSORDATA-MAX-AGE', '15'); # maximales Alter einer Temperaturmessung in Minuten
insert into pc_configuration (config_key, config_value) values ('SOLAR-MIN-RUNTIME', '5'); # minimale solar laufzeit bevor wieder abgeschalten werden kann
insert into pc_configuration (config_key, config_value) values ('MAXIMUM-POOL-TEMP', '22'); # max pool temp
