from flask import Flask, request
import RPi.GPIO as GPIO
import board
import busio
import adafruit_bme280
import threading
import time

FAN_PIN = 17
HEATER_PIN = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_PIN, GPIO.OUT)
GPIO.setup(HEATER_PIN, GPIO.OUT)

fan_pwm = GPIO.PWM(FAN_PIN, 1000)
fan_pwm.start(0)
GPIO.output(HEATER_PIN, GPIO.LOW)

i2c = busio.I2C(board.SCL, board.SDA)
bme = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)

target_temp = 22

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    global target_temp
    temp = bme.temperature
    humidity = bme.humidity

    html = f"""
    <h1>Smart Home Dashboard</h1>
    <p>Current Temp: {temp:.1f}°C</p>
    <p>Current Humidity: {humidity:.1f}%</p>
    <p>Target Temp: {target_temp}°C</p>

    <form method="POST">
        Set Target Temp (°C): <input type="number" name="target" value="{target_temp}">
        <input type="submit" value="Set">
    </form>
    """
    if request.method == "POST":
        try:
            target_temp = float(request.form["target"])
        except:
            pass
    return html

def control_loop():
    global target_temp
    while True:
        temp = bme.temperature
        error = temp - target_temp

        #ON/OFF
        if temp < target_temp - 0.5:
            GPIO.output(HEATER_PIN, GPIO.HIGH)
        elif temp > target_temp + 0.5:
            GPIO.output(HEATER_PIN, GPIO.LOW)

        fan_speed = max(0, min(100, error * 20))
        fan_pwm.ChangeDutyCycle(fan_speed)

        time.sleep(2)

thread = threading.Thread(target=control_loop)
thread.daemon = True
thread.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
