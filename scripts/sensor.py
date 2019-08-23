import constants

class Sensor:

    def __init__(self, sensor_location_id='', sensor_transmit_type='', sensor_model='', sensor_channel='', sensor_address='', temperatureunit=constants.TEMP_CELSIUS):
        self.sensor_location_id = sensor_location_id
        self.sensor_transmit_type = sensor_transmit_type
        self.sensor_model = sensor_model
        self.sensor_channel = sensor_channel
        self.sensor_address = sensor_address
        self.temperatureunit = temperatureunit


