import RPi.GPIO as GPIO
import board
import threading
import time
from adafruit_bme280 import basic as adafruit_bme280

# --- Configuration ---
FANPIN = 17
HEATERPIN = 27
target_temp = 25.0
running = True

# --- Hardware Setup ---
GPIO.setmode(GPIO.BCM)
GPIO.setup(FANPIN, GPIO.OUT)
GPIO.setup(HEATERPIN, GPIO.OUT)
GPIO.output(FANPIN, GPIO.LOW)
GPIO.output(HEATERPIN, GPIO.LOW)

# --- BME280 Setup (As requested) ---
i2c = board.I2C()
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
bme280.sea_level_pressure = 1013.25

def display_status():
    """Prints the temperature every second in the background."""
    global running, target_temp
    print("\n--- Experiment Started ---")
    print("Commands: 'fan on/off', 'heater on/off', 'target [value]', 'exit'\n")
    
    while running:
        temp = bme280.temperature
        fan_state = "ON" if GPIO.input(FANPIN) else "OFF"
        heat_state = "ON" if GPIO.input(HEATERPIN) else "OFF"
        
        # \r allows the line to overwrite itself for a clean look
        print(f"  [TEMP: {temp:.2f}°C] | [TARGET: {target_temp}°C] | [FAN: {fan_state}] | [HEATER: {heat_state}]    ", end='\r')
        time.sleep(1)

# Start the background display thread
status_thread = threading.Thread(target=display_status, daemon=True)
status_thread.start()

try:
    while True:
        # Get user command
        cmd = input().lower().strip()

        if cmd == "fan on":
            GPIO.output(FANPIN, GPIO.HIGH)
        elif cmd == "fan off":
            GPIO.output(FANPIN, GPIO.LOW)
        elif cmd == "heater on":
            GPIO.output(HEATERPIN, GPIO.HIGH)
        elif cmd == "heater off":
            GPIO.output(HEATERPIN, GPIO.LOW)
        elif cmd.startswith("target"):
            try:
                # Extracts the number from "target 25" or "target temp set 25"
                new_target = float(''.join(filter(lambda x: x.isdigit() or x == '.', cmd)))
                target_temp = new_target
            except ValueError:
                print("\nInvalid target format. Use 'target 25'")
        elif cmd == "exit":
            running = False
            break
        else:
            # If the user just hits enter, it won't break the display
            pass

except KeyboardInterrupt:
    running = False

finally:
    print("\nCleaning up GPIO and exiting...")
    GPIO.cleanup()