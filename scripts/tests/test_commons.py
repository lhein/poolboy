import unittest

from datetime import datetime
import commons

class CommonsTest(unittest.TestCase):

    def test_convertFahrenheit2Celsius(self):
        result = commons.convertFahrenheit2Celsius(90)
        self.assertEqual(result, 32.2, "Should be 32.2 but is " + str(result))

        result = commons.convertFahrenheit2Celsius(90)
        self.assertNotEqual(result, 35.6,
                            "Negative Test. Should be 32.2 but we check for 35.6 and result is " + str(result))

    def test_getCurrentTimestampAsString(self):
        nowMethod = commons.getCurrentTimestampAsString()
        nowSelf = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.assertEqual(nowMethod, nowSelf, "Values differ....slow PC or broken logic?")

        nowMethod = commons.getCurrentTimestampAsString()
        commons.waitSeconds(2)
        nowSelf = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.assertNotEqual(nowMethod, nowSelf, "Values should differ 2 seconds")

    def test_insideFilterSchedule(self):
        scheduleStart = '09:00'
        scheduleStop  = '12:00'

        currentTime = datetime.strptime('2019-08-09 08:59:59', '%Y-%m-%d %H:%M:%S')
        result = commons.insideFilterSchedule(scheduleStart, scheduleStop, currentTime)
        self.assertFalse(result, "We should be outside the filter schedule. Result should be False")

        currentTime = datetime.strptime('2019-08-09 09:00:00', '%Y-%m-%d %H:%M:%S')
        result = commons.insideFilterSchedule(scheduleStart, scheduleStop, currentTime)
        self.assertTrue(result, "We should be inside the filter schedule. Result should be True")

        currentTime = datetime.strptime('2019-08-09 12:00:00', '%Y-%m-%d %H:%M:%S')
        result = commons.insideFilterSchedule(scheduleStart, scheduleStop, currentTime)
        self.assertTrue(result, "We should be inside the filter schedule. Result should be True")

        currentTime = datetime.strptime('2019-08-09 12:01:00', '%Y-%m-%d %H:%M:%S')
        result = commons.insideFilterSchedule(scheduleStart, scheduleStop, currentTime)
        self.assertFalse(result, "We should be outside the filter schedule. Result should be False")

    def test_calculateDurationInMinutes(self):
        result = commons.calculateDurationInMinutes('2019-08-09 12:10:00', '2019-08-09 12:00:00')
        self.assertEqual(result, 10, "Duration should be 10 Minutes")

        result = commons.calculateDurationInMinutes('2019-08-09 12:00:00', '2019-08-08 12:00:00')
        self.assertEqual(result, 1440, "Duration should be 1440 Minutes == 1 day")

    def test_shouldFrostModeBeEnabled(self):
        enableLimit = 2
        disableLimit = 5

        # frost mode is currently active
        frostModeActive = True

        result = commons.shouldFrostModeBeActive(frostModeActive, enableLimit, disableLimit, 2, 5, 7)
        self.assertFalse(result, "From Pool to Solar water temp is 2 °C, which is lower than the disable limit for the frost mode....should return False")

        result = commons.shouldFrostModeBeActive(frostModeActive, enableLimit, disableLimit, 5, 5, 7)
        self.assertTrue(result,  "From Pool to Solar water temp is 5 °C, which is equal to the disable limit for the frost mode....should return True")

        result = commons.shouldFrostModeBeActive(frostModeActive, enableLimit, disableLimit, 7, 2, 5)
        self.assertFalse(result, "From Solar to Pool water temp is 2 °C, which is lower than the disable limit for the frost mode....should return False")

        result = commons.shouldFrostModeBeActive(frostModeActive, enableLimit, disableLimit, 7, 5, 5)
        self.assertTrue(result, "From Solar to Pool water temp is 5 °C, which is equal to the disable limit for the frost mode....should return True")

        result = commons.shouldFrostModeBeActive(frostModeActive, enableLimit, disableLimit, 7, 5, 2)
        self.assertFalse(result, "Solar panel air temp is 2 °C, which is lower than the disable limit for the frost mode....should return False")

        result = commons.shouldFrostModeBeActive(frostModeActive, enableLimit, disableLimit, 7, 5, 5)
        self.assertTrue(result,  "Solar panel air temp is 5 °C, which is equal to the disable limit for the frost mode....should return True")

        result = commons.shouldFrostModeBeActive(frostModeActive, enableLimit, disableLimit, -999.0, 5, 5)
        self.assertTrue(result, "From Pool to Solar water temp is UNKNOWN (-999.0), so one of the other values will be taken (all 5) which is equal to the disable limit for the frost mode....should return True")

        result = commons.shouldFrostModeBeActive(frostModeActive, enableLimit, disableLimit, -999.0, -999.0, 5)
        self.assertTrue(result, "Two water temps are UNKNOWN (-999.0), so the other value will be taken (5) which is equal to the disable limit for the frost mode....should return True")

        result = commons.shouldFrostModeBeActive(frostModeActive, enableLimit, disableLimit, -999.0, -999.0, -999.0)
        self.assertTrue(result, "All temps are UNKNOWN (-999.0)...should return True")

        # frost mode is currently not active
        frostModeActive = False

        result = commons.shouldFrostModeBeActive(frostModeActive, enableLimit, disableLimit, 2, 5, 7)
        self.assertTrue(result, "From Pool to Solar water temp is 2 °C, which is lower than the disable limit for the frost mode....should return False")

        result = commons.shouldFrostModeBeActive(frostModeActive, enableLimit, disableLimit, 5, 5, 7)
        self.assertFalse(result, "From Pool to Solar water temp is 5 °C, which is equal to the disable limit for the frost mode....should return True")

        result = commons.shouldFrostModeBeActive(frostModeActive, enableLimit, disableLimit, 7, 2, 5)
        self.assertTrue(result, "From Solar to Pool water temp is 2 °C, which is lower than the disable limit for the frost mode....should return False")

        result = commons.shouldFrostModeBeActive(frostModeActive, enableLimit, disableLimit, 7, 5, 5)
        self.assertFalse(result, "From Solar to Pool water temp is 5 °C, which is equal to the disable limit for the frost mode....should return True")

        result = commons.shouldFrostModeBeActive(frostModeActive, enableLimit, disableLimit, 7, 5, 2)
        self.assertTrue(result, "Solar temp is 2 °C, which is equal to the enable limit for the frost mode....should return True")

        result = commons.shouldFrostModeBeActive(frostModeActive, enableLimit, disableLimit, 7, 5, 5)
        self.assertFalse(result, "Solar temp is 5 °C, which is higher than the enable limit for the frost mode....should return False")

        result = commons.shouldFrostModeBeActive(frostModeActive, enableLimit, disableLimit, -999.0, 5, 5)
        self.assertFalse(result, "From Pool to Solar water temp is UNKNOWN (-999.0), so one of the other values will be taken (all 5) which is equal to the disable limit for the frost mode....should return True")

        result = commons.shouldFrostModeBeActive(frostModeActive, enableLimit, disableLimit, -999.0, -999.0, 5)
        self.assertFalse(result, "Two water temps are UNKNOWN (-999.0), so the other value will be taken (5) which is equal to the disable limit for the frost mode....should return True")

        result = commons.shouldFrostModeBeActive(frostModeActive, enableLimit, disableLimit, -999.0, -999.0, -999.0)
        self.assertTrue(result, "All temps are UNKNOWN (-999.0)...should return True")

    def test_isCoolingRequired(self):
        result = commons.isCoolingRequired(30, 20, 22, 2)
        self.assertFalse(result, "All water temps are lower than the max value. No Cooling required. Should Return False")

        result = commons.isCoolingRequired(30, 20, 22, 0)
        self.assertFalse(result, "All water temps are lower than the max value. No Cooling required. Should Return False")

        result = commons.isCoolingRequired(30, 30, 33, 2)
        self.assertTrue(result, "Poolwater temp is higher than the max value + delta. Cooling required. Should Return True")

        result = commons.isCoolingRequired(30, 33, 30, 2)
        self.assertFalse(result, "From Pool water temp is higher than the max value + delta. No cooling required because Pool Water has PRIO. Should Return False")

        result = commons.isCoolingRequired(30, 35, 33, 2)
        self.assertTrue(result, "All water temps are higher than the max value + delta. Cooling required. Should Return True")

        result = commons.isCoolingRequired(30, 30, 31, 0)
        self.assertTrue(result, "All water temps are higher than or equal the max value + delta. Cooling required. Should Return True")

        result = commons.isCoolingRequired(30, -999.0, -999.0, 2)
        self.assertFalse(result, "All water temps are unknown. Should Return False")

        result = commons.isCoolingRequired(30, -999.0, 20, 2)
        self.assertFalse(result, "From Pool to Solar water temp is unknown. Using the real pool water temp. Should Return False")

        result = commons.isCoolingRequired(30, -999.0, 33, 2)
        self.assertTrue(result, "From Pool to Solar water temp is unknown. Using the real pool water temp. Should Return True")

        result = commons.isCoolingRequired(30, 20, -999.0, 2)
        self.assertFalse(result, "Pool water temp is unknown. Using the temp from pool to solar. Should Return False")

        result = commons.isCoolingRequired(30, 33, -999.0, 2)
        self.assertTrue(result, "Pool water temp is unknown. Using the temp from pool to solar. Should Return True")

    def test_isCoolingPossible(self):
        #result = commons.isCoolingPossible(backflowtemp, solartemp, entryflowtemp, poolwatertemp, delta)
        delta = 2

        # hot summer day
        fromSolar = 45
        toSolar = 31
        water = 30
        solar = 50
        result = commons.isCoolingPossible(toSolar, fromSolar, solar, water, delta)
        self.assertFalse(result, "Today its too hot. Cooling impossible. Should return False")

        # hot summer day but poolwater sensor has no battery left
        fromSolar = 45
        toSolar = 31
        water = -999.0
        solar = 50
        result = commons.isCoolingPossible(toSolar, fromSolar, solar, water, delta)
        self.assertFalse(result, "Today its too hot. Cooling impossible. Should return False")

        # hot summer day but poolwater sensor has no battery left and water sensor for water going to solar is broken
        fromSolar = 45
        toSolar = -999.0
        water = -999.0
        solar = 50
        result = commons.isCoolingPossible(toSolar, fromSolar, solar, water, delta)
        self.assertFalse(result, "Not enough sensor data. Should return False")

        # hot summer day but sensor for water from solar to pool is broken
        fromSolar = -999.0
        toSolar = 31
        water = 32
        solar = 50
        result = commons.isCoolingPossible(toSolar, fromSolar, solar, water, delta)
        self.assertFalse(result, "Today its too hot. Cooling impossible. Should return False")

        # hot summer day but solar sensor and sensor for returning water from solar are broken
        fromSolar = -999.0
        toSolar = 31
        water = 32
        solar = -999.0
        result = commons.isCoolingPossible(toSolar, fromSolar, solar, water, delta)
        self.assertFalse(result, "Not enough sensor data. Should return False")

        # a cooler next day
        fromSolar = 20
        toSolar = 27
        water = 28
        solar = 22
        result = commons.isCoolingPossible(toSolar, fromSolar, solar, water, delta)
        self.assertTrue(result, "Today its much cooler. Cooling is possible. Should return True")

        # a near winter frosty day
        fromSolar = 12
        toSolar = 10
        water = 10
        solar = 15
        result = commons.isCoolingPossible(toSolar, fromSolar, solar, water, delta)
        self.assertFalse(result, "A really cold but sunny day. Cooling is not possible. Should return False")


    def test_getSolarRuntimeInMinutes(self):
        result = commons.getSolarRuntimeInMinutes('2019-08-08 10:00:00', '2019-08-08 10:10:00')
        self.assertEqual(result, 10, "10 Minutes Runtime is the correct value")

        result = commons.getSolarRuntimeInMinutes('2019-08-08 10:00:00', '2019-08-09 10:00:00')
        self.assertEqual(result, 1440, "1440 Minutes Runtime is the correct value")

    def test_isSolarMinimalRuntimeReached(self):
        result = commons.isSolarMinimalRuntimeReached(5, 0)
        self.assertFalse(result, "Min Runtime is not reached")

        result = commons.isSolarMinimalRuntimeReached(5, 4)
        self.assertFalse(result, "Min Runtime is not reached")

        result = commons.isSolarMinimalRuntimeReached(5, 5)
        self.assertTrue(result, "Min Runtime is reached")

        result = commons.isSolarMinimalRuntimeReached(5, 105)
        self.assertTrue(result, "Min Runtime is reached")

    def test_shouldSolarBeActivated(self):
        solarEnableDelta = 2
        maxPoolTemp = 30

        solarAbsorberTemp = 30
        toSolar = 18
        poolWater = 20
        result = commons.shouldSolarBeActivated(maxPoolTemp, solarEnableDelta, solarAbsorberTemp, toSolar, poolWater)
        self.assertTrue(result, "Temp delta is bigger than the enable delta. Should return True")

        solarAbsorberTemp = 30
        toSolar = 35
        poolWater = 20
        result = commons.shouldSolarBeActivated(maxPoolTemp, solarEnableDelta, solarAbsorberTemp, toSolar, poolWater)
        self.assertTrue(result, "Temp delta is bigger than the enable delta (Pool water temp has prio). Should return True")

        solarAbsorberTemp = 30
        toSolar = 35
        poolWater = -999.0
        result = commons.shouldSolarBeActivated(maxPoolTemp, solarEnableDelta, solarAbsorberTemp, toSolar, poolWater)
        self.assertFalse(result, "Poolwater sensor has no battery left. Water from pool to solar is hotter than max pool temp. Should return False")

        solarAbsorberTemp = 30
        toSolar = -999.0
        poolWater = -999.0
        result = commons.shouldSolarBeActivated(maxPoolTemp, solarEnableDelta, solarAbsorberTemp, toSolar, poolWater)
        self.assertFalse(result, "All water sensors are broken.Should return False")

        solarAbsorberTemp = -999.0
        toSolar = 35
        poolWater = 36
        result = commons.shouldSolarBeActivated(maxPoolTemp, solarEnableDelta, solarAbsorberTemp, toSolar, poolWater)
        self.assertFalse(result, "Sensor on solar absorber broken. Should return False")

    def test_shouldSolarBeDeactivated(self):
        solarDisableDelta = 2

        poolWaterTemp = 30
        fromSolar = 32
        solar = 35
        toSolar = 29
        result = commons.shouldSolarBeDeactivated(poolWaterTemp, toSolar, solar, fromSolar, solarDisableDelta)
        self.assertTrue(result, "Delta hit. Should deactivate.")

        poolWaterTemp = 30
        fromSolar = 34
        solar = 35
        toSolar = 29
        result = commons.shouldSolarBeDeactivated(poolWaterTemp, toSolar, solar, fromSolar, solarDisableDelta)
        self.assertFalse(result, "Delta not hit. Should stay active.")

        poolWaterTemp = -999.0
        fromSolar = 32
        solar = 35
        toSolar = 30
        result = commons.shouldSolarBeDeactivated(poolWaterTemp, toSolar, solar, fromSolar, solarDisableDelta)
        self.assertTrue(result, "Delta hit. Should deactivate.")

        poolWaterTemp = 30
        fromSolar = -999.0
        solar = 35
        toSolar = 30
        result = commons.shouldSolarBeDeactivated(poolWaterTemp, toSolar, solar, fromSolar, solarDisableDelta)
        self.assertFalse(result, "Delta not hit. Should stay active.")

        poolWaterTemp = 30
        fromSolar = -999.0
        solar = -999.0
        toSolar = 30
        result = commons.shouldSolarBeDeactivated(poolWaterTemp, toSolar, solar, fromSolar, solarDisableDelta)
        self.assertTrue(result, "No sensor data for water flow back to pool. Should deactivate.")

        poolWaterTemp = -999.0
        fromSolar = 35
        solar = 40
        toSolar = -999.0
        result = commons.shouldSolarBeDeactivated(poolWaterTemp, toSolar, solar, fromSolar, solarDisableDelta)
        self.assertTrue(result, "No sensor data for water flow to solar. Should deactivate.")
