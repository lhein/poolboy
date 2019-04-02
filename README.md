# Poolboy
Raspberry Pi based Pool Controller

## Features
* collect temperatures from a number of sensors and store them
* collect humidity of sensors if supported
* check battery status of sensors and issue warning / alert if battery is low
* daily pump scheduling
* configure max pool water temperature
* configure temperature deltas for enabling / disabling solar heating
* configure a min temp for the pool water for anti frost mode -> will result in pumping to prevent frost damage
* override capabilities for pump whenever pool is too cold and temp delta is fine
* manual override to disable / enable solar heating
* manual override to disable / enable pool pump
* manual switch for enabling / disabling automatic pool control
* automatic frost securing in automatic mode
* cooling an overheated pool depending on temperatures in automatic mode

### Features in planning
* sensor calibration
* multi language support (german / english for now)
* collect data from a water throughput sensor and store it
* configure a min and a max water throughput (maybe depending on temperature / season / month)
* ...

## Data Storage
* MySQL / MariaDB
* leverages MQTT for transmitting data from sensors to a dedicated sensor data processor

## Programming
* Language: Python
* Invocation: Cron

## GUI
Development of a graphical user interface for the pool controller. 

### Planned Features
* show a dashboard with useful data (temps, operational modes of pump, solar, etc)
* buttons for manipulating operational modes
* dedicated area for displaying Alerts
* statistics feature for temperatures
* statistics feature for operational mode changes / hardware mode changes
* statistics feature for runtimes (pump, solar, maybe throughput of water)
* admin page for manipulating configuration values
* admin page for calibrating sensors
* admin page for viewing event logs
* multi language support (german / english for now)

### Web UI 
* React based Web UI

### Android / iPhone App
* ...

