import time
import servicelayer

debugMode = True

def log(msg):
    if debugMode:
        print(msg)

def mainLoop():

    ############################################
    ### EMERGENCY MODE HANDLING 
    ############################################

    log("Determine if we are in Emergency Mode")
    if servicelayer.isEmergencyModeActive():
        log("Emergency Mode is active! Waiting for operator to fix problem! No further logic executed! Exiting!")
        servicelayer.activateEmergencyMode()
        return
    else:
        log("Emergency Mode is NOT active! Continue...")
        servicelayer.deactivateEmergencyMode()


    # we remember if we changed the solar state before (don' change more than once per cylce
    solarStateChangedLately = False


    ############################################
    ### AUTOMATIC MODE HANDLING 
    ############################################

    log("Determine if we are in Automatic Mode")
    if servicelayer.isAutomaticModeActive():
        log("Automatic Mode is active!")
        servicelayer.activateAutomaticMode()

        #################################################
        ### FROST MODE HANDLING - ONLY IN AUTOMATIC MODE
        #################################################

        # check if frostmode should be enabled
        if servicelayer.shouldFrostModeBeActivated():
            log("Danger! Frost! Activating Pump and Solar...")
            servicelayer.activateFrostMode()
            log("We are now in Frost Mode. No other logic executed. Exiting...")
            return
        else:
            log("No Frost Danger...")
            if servicelayer.isFrostModeActive():
                log("Frost Mode no longer required...deactivating...")
                servicelayer.deactivateFrostMode()


        #####################################################################################
        ### FILTER MODE HANDLING - ONLY IN AUTOMATIC MODE
        #####################################################################################
        #
        # When to activate filter pump?
        #    insideFilterSchedule AND maxDailyRuntimeNotReached -> normal filter schedule
        #  OR
        #    HeatingOverrideActive AND shouldSolarBeActivated -> heating active
        #####################################################################################

        # filter pump activation
        log("Determine if filter pump can be activated...")
        if  servicelayer.isInsideFilterSchedule() or \
            servicelayer.isFilterOverrideModeActive() and servicelayer.shouldSolarBeActivated():

            # log the mode to console
            if servicelayer.isInsideFilterSchedule():
                log("Filter Period Scheduled!")
            else:
                log("Filter Override Mode active!")

            if not servicelayer.isFilterPumpActive():
                servicelayer.activateFilterPump()
            else:
                log("Filter already active...")

        else: # outside filter schedule AND no override active
            
            log("Not inside filter schedule times.")

        #####################################################################################
        ### SOLAR MODE HANDLING - ONLY IN AUTOMATIC MODE
        #####################################################################################
        #
        # When to activate solar in general?
        #
        #    shouldSolarBeActivated and not isSolarActive
        #    
        #####################################################################################

        # solar enablement handling
        log("Determine if solar can be activated...")
        if not servicelayer.isSolarActive() and servicelayer.shouldSolarBeActivated():

            ###########################################################################
            # Conditions for NOT activating
            ###########################################################################
            #
            #     solarStateChangedLately
            #  OR
            #     NOT headtingOverRideActive 
            #  AND
            #     maxDailyRuntimeReached OR NOT insideFilterSchedule
            #
            ###########################################################################

            if solarStateChangedLately or \
                not servicelayer.isFilterOverrideModeActive() and not servicelayer.isInsideFilterSchedule():

                # there is no reason to activate solar and pump
                log('Conditions for enabling Solar are not met!')
                if solarStateChangedLately:
                    log("Solar State has been changed already in this cycle...")
                else:
                    log("Outside the filter schedule while Filter Override is deactivated...")

            else:

                log("Solar should be activated...")
                if not servicelayer.isFilterPumpActive():
                    servicelayer.activateFilterPump()

                servicelayer.activateSolar()
                solarStateChangedLately = True

        else:
            # log some output to console
            if servicelayer.isSolarActive():
                log("Solar is already active...")
            else:
                log("Not enough solar heat...")

        #####################################################################################
        ### SOLAR MODE HANDLING - ONLY IN AUTOMATIC MODE
        #####################################################################################

        # Solar Disable Handler
        log("Determine if solar should be deactivated...")
        if servicelayer.isSolarActive() and servicelayer.shouldSolarBeDeactivated():
            # solar mode is active

            #########################################################################
            # When to deactivate?
            #########################################################################
            # 
            #     filter pump active 
            #  AND 
            #     NOT cooler mode active
            #  AND
            #     minSolarRuntimeReached
            # 
            #########################################################################


            if servicelayer.isFilterPumpActive() and \
                not servicelayer.isCoolerModeActive() and \
                servicelayer.isSolarMinRuntimeReached():

                log("Solar Mode should be deactivated")
                if not solarStateChangedLately:
                    # deactivate solar 
                    servicelayer.deactivateSolar()
                    log("Solar deactivated!")
                    # check if inside filter schedule
                    if servicelayer.isFilterPumpActive() and not servicelayer.isInsideFilterSchedule():
                        log("Filter pump was active. Deactivating...")
                        servicelayer.deactivateFilterPump()
                else:
                    log("Solar State has been changed already in this cycle...")
            else:
                if servicelayer.isSolarMinRuntimeReached():
                    log("Minimal Solar Runtime not yet reached. Keep Solar running...")
                elif servicelayer.isCoolerModeActive():
                    log("Cooler Mode is currently active. Keep Solar running...")
        else:
            if not servicelayer.isSolarActive():
                # solar mode is already deactivated
                log("Solar is not active. No actions required.")
            else:
                log("Solar should stay activated...")


        #####################################################################################
        ### COOLER MODE HANDLING - ONLY IN AUTOMATIC MODE
        #####################################################################################

        # cooling mode handler
        log("Determine if Cooler Mode should be activated...")
        if servicelayer.isCoolingRequired() and servicelayer.isCoolingPossible() and (servicelayer.isFilterOverrideModeActive() or servicelayer.isInsideFilterSchedule()):
            log("Pool water too warm!")

            # check if cooling possible and not yet active
            if not servicelayer.isCoolerModeActive():
                log("Activating cooler mode...")
                servicelayer.activateCoolerMode()
            else:
                log("Cooler Mode already active...")

            # activate solar absorbers if needed
            if not servicelayer.isSolarActive() and servicelayer.isSolarMinimalRuntimeReached() and not solarStateChangedLately:
                log("Activating Solar Absorbers...")
                servicelayer.activateSolar()
                if not servicelayer.isFilterPumpActive():
                    servicelayer.activateFilterPump()
        else:
            if not servicelayer.isCoolingPossible() and servicelayer.isCoolingRequired():
                log("Solar temperature too high. No cooling possible!")
                if servicelayer.isCoolerModeActive():
                    servicelayer.deactivateCoolerMode()
            elif not servicelayer.isFilterOverrideModeActive() or not servicelayer.isInsideFilterSchedule():
                log("Not inside filter schedule and filter override mode is not active.")
            else:
                log("No Cooling required!")

        #####################################################################################
        ### CHECK IF THE PUMP IS STILL RUNNING AND CAN BE DEACTIVATED
        #####################################################################################
        log("Checking if Filter Pump is running and should be deactivated...")
        if not servicelayer.isInsideFilterSchedule() and servicelayer.isFilterPumpActive():
            log("Filter Pump is running outside scheduled times...")
            if servicelayer.isCoolerModeActive():
                log("Cooling mode active...Keep pump running...")
            elif servicelayer.isSolarActive() and servicelayer.shouldSolarBeActivated():
                log("Solar Heater active...Keep pump running...")
            else:
                log("No reason to run the pump....deactivating...")
                # disable pump
                servicelayer.deactivateFilterPump()
        else:
            if not servicelayer.isFilterPumpActive():
                log("Pump is not active...")
            else:
                log("We are in scheduled filter time...")

    else:
        log("Automatic Mode is not active! Skipping all logic!")

        #################################################
        ### MANUAL FILTER MODE HANDLING
        #################################################

        log("Determine Manual Filter Override Mode status...")
        if servicelayer.isManualFilterModeActive():
            log("Manual Filter Mode is active...")
            servicelayer.activateManualFilterMode()
        else:
            log("Manual Filter Mode is not active...")
            servicelayer.deactivateManualFilterMode()

        #################################################
        ### MANUAL SOLAR MODE HANDLING
        #################################################

        log("Determine Manual Solar Override Mode status...")
        if servicelayer.isManualSolarModeActive():
            log("Manual Solar Mode is active...")
            servicelayer.activateManualSolarMode()
        else:
            log("Manual Solar Mode is not active...")
            servicelayer.deactivateManualSolarMode()

    #################################################
    ### END OF MAIN LOOP
    #################################################


loop_interval = 60 # 60 secs loop interval
servicelayer.init()

while True:
    log(">>> CYCLE START >>>")
    mainLoop()
    log("<<< CYCLE END <<<")
    time.sleep(loop_interval);

