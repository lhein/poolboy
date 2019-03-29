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

if dbcontrol.getWinterMode() == constants.ON:
    print('Wintermodus!')
    if gpioutils.getFilterPumpState() == constants.ON:
        print('Filterpumpe läuft noch...deaktiviere...')
        gpioutils.deactivateFilterPump()
        print('Filterpumpe deaktiviert. Protokolliere Endzeit und Laufzeit der Pumpe')
        if gpioutils.getSolarState() == constants.ON:
            print('Solar-Bypass bereits offen. Protokolliere Endzeit und Laufzeit des Solarabsorbers')
    if gpioutils.getSolarState() == constants.OFF:
        print('Solar-Bypass ist geschlossen! Öffne den Bypass...')
        gpioutils.activateSolar()
        print('Solar-Bypass ist jetzt offen.')

    gpioutils.deactivateAutomaticMode()
    gpioutils.deactivateManualFilterMode()
    gpioutils.deactivateManualSolarMode()
    gpioutils.activateWinterMode()

    sys.exit()
else:
    gpioutils.deactivateWinterMode()

solarStateChanged = False

# enabled automatic mode of filter override off and winter off
if gpioutils.getAutomaticModeState() == constants.OFF and gpioutils.getManualFilterModeState() == constants.OFF and dbcontrol.getWinterMode() == constants.OFF:
    print("STARTE AUTOMATIC MODE")
    gpioutils.activateAutomaticMode()

# wenn innerhalb zeitfenster && pumpe inaktiv && tageslaufzeit nicht erreicht && automatic an gpio = ON
if utils.insideFilterSchedule() == True and \
   utils.maxDailyFilterRuntimeReached() == False and \
   gpioutils.getAutomaticModeState() == constants.ON:
    print('Filterzeit!')
    if (gpioutils.getFilterPumpState() == constants.OFF):
        gpioutils.activateFilterPump()
        print('Filterpumpe aktiviert. Protokolliere Startzeit der Pumpe')
        if gpioutils.getSolarState() == constants.ON:
            print('Solarabsorber aktiviert. Protokolliere Startzeit')
else: 
    print("Nanu? Keine Filterzeit!")
    if (gpioutils.getFilterPumpState() == constants.ON):
        print("Pumpe noch aktiv! Deaktiviere Pumpe!")
        gpioutils.deactivateFilterPump()
        print('Filterpumpe deaktiviert. Protokolliere Endzeit und Laufzeit der Pumpe')

# wenn solardelta >= minSolarDelta && !manualSolarMode && automatic
if gpioutils.getSolarState() == constants.OFF and utils.shouldSolarBeActivated() and gpioutils.getManualSolarModeState() == constants.OFF and gpioutils.getAutomaticModeState() == constants.ON:
    print("Solar sollte zugeschaltet werden")
    if gpioutils.getFilterPumpState() == constants.OFF:
        gpioutils.activateFilterPump()
        print('Filterpumpe aktiviert. Protokolliere Startzeit der Pumpe')
    
    gpioutils.activateSolar()
    print('Solarabsorber aktiviert. Protokolliere Startzeit')
    solarStateChanged = True

# wenn pumpe aktiv && solar aktiv && !manuellerSolarMode && solarDelta < hysteresis (minimalErtrag)
if gpioutils.getSolarState() == constants.ON and gpioutils.getFilterPumpState() == constants.ON and utils.shouldSolarBeDeactivated() and gpioutils.getManualSolarModeState() == constants.OFF and gpioutils.getAutomaticModeState() == constants.ON:
    print("Solar sollte abgeschaltet werden")
    if solarStateChanged == False:
        gpioutils.deactivateSolar()
        print('Solar deaktiviert. Protokolliere Endzeit und Laufzeit')
    else:
        print('Solar wird im nächsten Zyklus deaktiviert um den Motor zu schonen. (keine mehrfachen Zustandsänderungen in einem einzigen Zyklus!)')


