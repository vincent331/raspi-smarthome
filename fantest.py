import RPi.GPIO as GPIO
import time
FAN_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_PIN, GPIO.OUT)

fan_pwm = GPIO.PWM(FAN_PIN, 1000)#1khz, who knows?
fan_pwm.start(0)

try:
    while True:
        speed = int(input("Enter fan speed"))
        speed = max(0, min(100, speed))
        fan_pwm.ChangeDutyCycle(speed)
        print(f"Fan at {speed}%")

except KeyboardInterrupt:
    print("Stopping fan")
    fan_pwm.stop()
    GPIO.cleanup()
