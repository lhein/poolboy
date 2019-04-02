#################################################################################################################################################
#																		#
# 	POOLBOY - Script zum Steuern der Pumpe und des Solarabsorbers										#
#																		#
#################################################################################################################################################
#																		#
#	FUNKTIONSWEISE:																#
#																		#
#	// bei wintermode alles aus und solar auf												#
#	wenn DB wintermodus															#
#		-> wenn Pumpe an														#
#			-> pumpe aus														#
#			-> endzeit und laufzeit protokollieren											#
#			-> wenn Solar an													#
#				-> endzeit und laufzeit protokollieren										#
#		-> wenn Solar zu														#
#			-> solar aufmachen, keine startzeit protokollieren									#
#		-> Automatik deaktivieren													#
#		-> Manuelles Filter aus														#
#		-> Manuelles Solar aus														#
#		-> Wintermodus aktivieren													#
#																		#
#       // automatik im zeitfenster bei nicht erreichter max laufzeit										#
# 	wenn innerhalb zeitfenster && pumpe inaktiv && tageslaufzeit nicht erreicht && automatic an gpio = ON					#
# 		-> pumpe starten														#
#               -> startzeit der pumpe in db festhalten												#
#																		# 
# 	// solar override im automatic modus (auch bei inaktiver pumpe)										#
#       wenn solardelta >= minSolarDelta && !manualSolarMode && automatic									#
#               -> wenn pumpe inaktiv														# 
#	 		-> pumpe starten													#
#       	        -> startzeit der pumpe in db festhalten											#
#		-> solar aktivieren														#
#               -> startzeit solar in db festhalten												#
#																		# 
# 	// abschalten von solar sobald kein Ertrag mehr möglich ist und die pumpe noch läuft und kein manueller solarmode aktiv			#
# 	wenn pumpe aktiv && solar aktiv && !manuellerSolarMode && solarDelta < hysteresis (minimalErtrag)					#
# 		-> solar deaktiveren														#
# 		-> stopzeit in db festhalten													#
# 		-> solarlaufzeit in db addieren													#
# 																		#
#################################################################################################################################################
import sys
import time

import constants # our own constants def file
import dbcontrol # our own db utils file
import gpioutils
import utils # our own utils file

# init gpio
gpioutils.init()

# Emergency Case Handler
if dbcontrol.getEmergencyMode() == constants.ON_STRING:
    print('Not-Aus aktiv! Bitte zuerst Fehler beheben und Not-Aus quittieren.')
    gpioutils.activateEmergencyMode()
    if gpioutils.getFilterPumpState() == constants.ON:
        print('Filterpumpe läuft noch...deaktiviere...')
        gpioutils.deactivateFilterPump()
        print('Filterpumpe deaktiviert. Protokolliere Endzeit und Laufzeit der Pumpe')
    if gpioutils.getSolarState() == constants.ON:
        print('Solar-Bypass ist noch offen! Schliesse den Bypass...')
        gpioutils.deactivateSolar()
        print('Solar-Bypass ist jetzt geschlossen.')

    gpioutils.deactivateAutomaticMode()
    gpioutils.deactivateManualFilterMode()
    gpioutils.deactivateManualSolarMode()
    sys.exit()
else:
    gpioutils.deactivateEmergencyMode()

# we remember if we changed the solar state before (don' change more than once per cylce
solarStateChanged = False

# we only run automated control logic when Automatic is ON
if gpioutils.getAutomaticModeState() == constants.ON or dbcontrol.getAutomaticMode() == constants.ON_STRING:
    if gpioutils.getAutomaticModeState() == constants.OFF:
        gpioutils.activateAutomaticMode()
    # remember we are in automatic mode
    dbcontrol.updateAutomaticMode(constants.ON_STRING)

    # active Frost Mode Handler
    if dbcontrol.getFrostMode() == constants.ON_STRING:
        print('Frostschutzmodus!')
        if gpioutils.getFilterPumpState() == constants.OFF:
            print('Filterpumpe offline...aktiviere...')
            gpioutils.activateFilterPump()
            print('Filterpumpe aktiviert. Protokolliere Endzeit und Laufzeit der Pumpe')
        if gpioutils.getSolarState() == constants.OFF:
            print('Solar-Bypass ist geschlossen! Öffne den Bypass...')
            gpioutils.activateSolar()
            print('Solar-Bypass ist jetzt offen.')

        gpioutils.deactivateManualFilterMode()
        gpioutils.deactivateManualSolarMode()
        gpioutils.activateFrostMode()

        sys.exit()
    else:
        gpioutils.deactivateFrostMode()


    # check if frostmode should be enabled
    if utils.shouldFrostModeBeEnabled():
        print('Achtung Frostgefahr!')
        if gpioutils.getFrostModeState() == constants.OFF:
            gpioutils.activateFrostMode()
            if (gpioutils.getFilterPumpState() == constants.OFF):
                gpioutils.activateFilterPump()
                print('Filterpumpe aktiviert. Protokolliere Startzeit der Pumpe')
            if (gpioutils.getSolarState() == constants.OFF):
                gpioutils.activateSolar()
                print('Solarabsorber aktiviert. Protokolliere Startzeit')
        sys.exit()
    elif not utils.shouldFrostModeBeEnabled and gpioutils.getFrostModeState() == constants.ON:
        print('Keine Frostgefahr mehr! Deaktiviere Pumpe und Solar.')
        gpioutils.deactivateFrostMode()
        sys.exit()

    # Filter Activation Handler
    if utils.insideFilterSchedule() == True and \
       utils.maxDailyFilterRuntimeReached() == False:
        print('Filterzeit!')
        if (gpioutils.getFilterPumpState() == constants.OFF):
            gpioutils.activateFilterPump()
            print('Filterpumpe aktiviert. Protokolliere Startzeit der Pumpe')
    else: 
        print("Keine Filterzeit!")
        if (dbcontrol.getHeatingOverrideMode() == constants.OFF_STRING and \
            gpioutils.getFilterPumpState() == constants.ON):
            print("Pumpe noch aktiv! Deaktiviere Pumpe!")
            gpioutils.deactivateFilterPump()
            print('Filterpumpe deaktiviert. Protokolliere Endzeit und Laufzeit der Pumpe')
            if solarStateChanged == False:
                gpioutils.deactivateSolar()
                solarStateChanged = True
                print('Solar deaktiviert. Protokolliere Endzeit und Laufzeit')
            else:
                print('Solar wird im nächsten Zyklus deaktiviert um den Motor zu schonen. (keine mehrfachen Zustandsänderungen in einem einzigen Zyklus!)')

    # Solar Enablement Handler
    if gpioutils.getSolarState() == constants.OFF and \
       utils.shouldSolarBeActivated() and \
       dbcontrol.getHeatingOverrideMode() == constants.ON_STRING and \
       (gpioutils.getManualSolarModeState() == constants.OFF or utils.maxDailyFilterRuntimeReached() == False):
        print("Solar sollte zugeschaltet werden")
        if solarStateChanged == False:
            if gpioutils.getFilterPumpState() == constants.OFF:
                gpioutils.activateFilterPump()
                print('Filterpumpe aktiviert. Protokolliere Startzeit der Pumpe')
            gpioutils.activateSolar()
            print('Solarabsorber aktiviert. Protokolliere Startzeit')
            solarStateChanged = True

    # Solar Disable Handler
    if gpioutils.getSolarState() == constants.ON and \
       gpioutils.getFilterPumpState() == constants.ON and \
       gpioutils.getCoolerModeState() == constants.OFF and \
       utils.shouldSolarBeDeactivated() and \
       gpioutils.getManualSolarModeState() == constants.OFF:
        print("Solar sollte abgeschaltet werden")
        if solarStateChanged == False:
            gpioutils.deactivateSolar()
            print('Solar deaktiviert. Protokolliere Endzeit und Laufzeit')
            if (gpioutils.getFilterPumpState() == constants.ON and utils.insideFilterSchedule() == False):
                gpioutils.deactivateFilterPump()
                print('Filterpumpe deaktiviert. Protokolliere Laufzeit')
        else:
            print('Solar wird im nächsten Zyklus deaktiviert um den Motor zu schonen. (keine mehrfachen Zustandsänderungen in einem einzigen Zyklus!)')

    # cooling mode handler
    if utils.isCoolingRequired():
        print("Poolwasser zu warm!")
        if utils.isCoolingPossible():
            print("Kühlungsmodus aktivieren!")
            gpioutils.activateCoolerMode()
            if gpioutils.getSolarState() == constants.OFF:
                gpioutils.activateSolar()
                print('Solarabsorber aktiviert. Protokolliere Startzeit')
            if gpioutils.getFilterPumpState() == constants.OFF:
                gpioutils.activateFilterPump()
                print('Filterpumpe aktiviert. Protokolliere Startzeit der Pumpe')
        else:
            print("Solartemperatur zu hoch. Derzeit keine Kühlung möglich!")
            if gpioutils.getCoolerModeState() == constants.ON:
                print("Deaktiviere Kuehlungsmodus...")
                gpioutils.deactivateCoolerMode()
    else:
        print("Poolwasser nicht zu warm!")
        
else:
    print("Automatik ist AUS! Nichts zu tun...")

