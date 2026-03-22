from flask import Flask, request, render_template, jsonify
import RPi.GPIO as GPIO
import board
import busio
import adafruit_bme280
import threading
import time
from sklearn.neural_network import MLPRegressor
import csv
import os
import pickle
import numpy as np
from sklearn.preprocessing import LabelEncoder


if not os.path.exists('experimentdata.csv'):
    with open('experimentdata.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['temp1', 'temp2', 'heater1', 'heater2', 'fan1', 'fan2', 'target_temp'])

FANPIN1 = 17
FANPIN2 = 18
HEATERPIN1 = 27
HEATERPIN2 = 28

GPIO.setmode(GPIO.BCM)
GPIO.setup(FANPIN1, GPIO.OUT)
GPIO.setup(HEATERPIN1, GPIO.OUT)
GPIO.setup(FANPIN2, GPIO.OUT)
GPIO.setup(HEATERPIN2, GPIO.OUT)

fanpwm1 = GPIO.PWM(FANPIN1, 1000)
fanpwm2 = GPIO.PWM(FANPIN2, 1000)
fanpwm1.start(0)
fanpwm2.start(0)
GPIO.output(HEATERPIN1, GPIO.LOW)
GPIO.output(HEATERPIN2, GPIO.LOW)

i2c = board.I2C()
bme1 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
bme2 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x77) #double check ts

app = Flask(__name__)

@app.route('/')
def home():
    t1 = bme1.temperature
    t2 = bme2.temperature   
    return render_template('dashboard.html',
                           temp1=round(t1,2),
                           temp2=round(t2,2),
                           fan1=fanpwm1.duty_cycle if hasattr(fanpwm1, 'duty_cycle') else 0,
                           fan2=fanpwm2.duty_cycle if hasattr(fanpwm2, 'duty_cycle') else 0,
                           heater1=GPIO.input(HEATERPIN1),
                           heater2=GPIO.input(HEATERPIN2),
                           target_temp=target_temp)

@app.route('/set_target', methods=['POST'])
def set_target():
    global target_temp
    data = request.form
    target_temp = float(data['target'])
    return jsonify({'status':'ok', 'target': target_temp})

@app.route('/control_device', methods=['POST'])
def control_device():
    data = request.json
    device = data['device']
    state = data['state']

    if device == 'fan1':
        fanpwm1.ChangeDutyCycle(int(state))
    elif device == 'fan2':
        fanpwm2.ChangeDutyCycle(int(state))
    elif device == 'heater1':
        GPIO.output(HEATERPIN1, GPIO.HIGH if state == "on" else GPIO.LOW)
    elif device == 'heater2':
        GPIO.output(HEATERPIN2, GPIO.HIGH if state == "on" else GPIO.LOW)

    return jsonify({'status':'ok'})

@app.route('/api/temps')
def temps():
    return jsonify({
        'temp1': round(bme1.temperature,2),
        'temp2': round(bme2.temperature,2),
        'fan1': fanpwm1.duty_cycle if hasattr(fanpwm1, 'duty_cycle') else 0,
        'fan2': fanpwm2.duty_cycle if hasattr(fanpwm2, 'duty_cycle') else 0,
        'heater1': GPIO.input(HEATERPIN1),
        'heater2': GPIO.input(HEATERPIN2),
        'target_temp': target_temp
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

    