import RPi.GPIO as GPIO
import time

HEATER_PIN = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(HEATER_PIN, GPIO.OUT)
GPIO.output(HEATER_PIN, GPIO.LOW)

try:
    while True:
        command = input("on/off").strip().lower()

        if command == "on":
            GPIO.output(HEATER_PIN, GPIO.HIGH)
            print("ON")

        elif command == "off":
            GPIO.output(HEATER_PIN, GPIO.LOW)
            print("Heater OFF")

        else:
            print("n/a")

except KeyboardInterrupt:
    print("Shutting down")
    GPIO.output(HEATER_PIN, GPIO.LOW)
    GPIO.cleanup()
