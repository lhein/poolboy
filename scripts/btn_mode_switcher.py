import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BCM) # Use physical pin numbering

GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP) # MANUAL FILTER
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP) # AUTOMATIC
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP) # MANUAL SOLAR
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP) # WINTER MODE

AUTO = 23
MAN_FILTER = 24
MAN_SOLAR = 25
WINTER = 26

GPIO.setup(AUTO, GPIO.IN)
GPIO.setup(MAN_FILTER, GPIO.IN)
GPIO.setup(MAN_SOLAR, GPIO.IN)
GPIO.setup(WINTER, GPIO.IN)

v_AUTO = GPIO.input(AUTO)
v_FILTER = GPIO.input(MAN_FILTER)
v_SOLAR = GPIO.input(MAN_SOLAR)
v_WINTER = GPIO.input(WINTER)

def button_callback(channel):
    print("Button was pushed! ", channel)

    if channel == 6:
        global v_AUTO
        switchMode(AUTO, v_AUTO)
        v_AUTO = not v_AUTO
    elif channel == 5:
        global v_FILTER
        switchMode(MAN_FILTER, v_FILTER)
        v_FILTER = not v_FILTER
    elif channel == 17:
        global v_SOLAR
        switchMode(MAN_SOLAR, v_SOLAR)
        v_SOLAR = not v_SOLAR
    elif channel == 18:
        global v_WINTER
        switchMode(WINTER, v_WINTER)
        v_WINTER = not v_WINTER

def switchMode(gpio, value):
    GPIO.setup(gpio, GPIO.OUT)
    GPIO.output(gpio, value)

GPIO.add_event_detect(5, GPIO.RISING, callback=button_callback) # Setup event on pin 10 rising edge
GPIO.add_event_detect(6, GPIO.RISING, callback=button_callback) # Setup event on pin 10 rising edge
GPIO.add_event_detect(17, GPIO.RISING, callback=button_callback) # Setup event on pin 10 rising edge
GPIO.add_event_detect(18, GPIO.RISING, callback=button_callback) # Setup event on pin 10 rising edge

message = input("Press enter to quit\n\n") # Run until someone presses enter
GPIO.cleanup() # Clean up


