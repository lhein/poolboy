# raspi-poolcontroller
Raspberry Pi based Pool Controller

## Features
* collect temperatures from a number of sensors and store them
* collect humidity of sensors if supported
* check battery status of sensors and issue warning / alert if battery is low -> maybe additional alert email
* collect data from a water throughput sensor and store it
* daily pump scheduling
* configure a min and a max water throughput (maybe depending on temperature / season / month)
* configure max pool water temperature
* configure min temperature delta between pool water and solar heater sensor to enable solar heating
* configure hysteresis for enabling / disabling solar heating
* configure a min temp for the pool water for anti frost mode -> will result in pumping to prevent frost damage
* override capabilities for pump whenever pool is too cold and temp delta is fine
* manual override to disable / enable solar heating
* manual override to disable / enable pool pump
* manual switch for enabling / disabling automatic pool control
* automatic frost securing

## Programming
* Language: Python
* Invocation: Cron

### Scripts
* Raspberry Startup
* PoolMainController
* 

## GUI

Development of a graphical user interface for the pool controller. All temperatures should be displayed, there should be lights and buttongs for the different modes (pump, solar, auto, manual, frostsafe etc). The UI should also allow to modify the configuration values, recalibrate sensors?, visit statistics both graphical and textual, view the logs of the application.

### Web UI 

### Android / iPhone App


## Data Storage

### Database
We will use a mySql database to store values and logs.

### Tables

#### events (based on different event types)
* id
* timestamp
* source (gpio or a defined id string)
* type (debug / info / warning / error)
* data (the event data - could be a message or values from some sensor (we need to define a fixed format for those)

#### configuration
* key
* value
* defaultValue
* valueType (boolean, string, number, time, date, duration?)
* description
