# Poolboy
Raspberry Pi based Pool Controller

## Features
* collect temperatures from a number of sensors
* collect humidity from a number of sensors (if supported)
* check battery status of sensors and issue warning / alert if battery is low
* daily pump scheduling (free configurable multiple schedules)
* configure max pool water temperature
* cooling an overheated pool depending on temperatures in automatic mode
* configure temperature deltas for enabling / disabling solar heating
* automatic frost safe mode when in automatic mode
* configure a minimum temperature for pool water for frost mode -> will result in pumping to prevent frost damage
* override capabilities for pool heating / cooling
* manual override to disable / enable solar heating
* manual override to disable / enable pool pump
* manual switch for enabling / disabling automatic pool control
* emergency mode for hard failures in HW or configuration / events / alerts

### Features in planning
* sensor calibration
* multi language support (german / english for now)
* determine filter pressure / signal need for backwashing / calibration of pressure
* ...

## Data Storage
* MySQL / MariaDB

## Programming
* Language: Python
* Invocation: Cron

## GUI
Development of a web based graphical user interface for the pool controller. 

### Planned Features
* show a dashboard with useful data (temps, operational modes of pump, solar, etc)
* buttons for manipulating operational modes
* dedicated area for displaying Alerts / Events
* statistics feature for temperatures, pressure, etc.
* statistics feature for operational mode changes / hardware mode changes
* statistics feature for runtimes (pump, solar)
* admin page for manipulating configuration values
* admin page for calibrating sensors
* admin page for viewing event logs
* admin page for manipulating filter schedules
* admin page for manipulating installed sensors
* multi language support (german / english for now)

### Web UI 
* React based Web UI

### Android / iPhone App
* ...

