from flask import Flask, request, render_template, jsonify
import RPi.GPIO as GPIO
import board
import threading
import time
from adafruit_bme280 import basic as adafruit_bme280

app = Flask(__name__)

FANPIN    = 17
HEATERPIN = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(FANPIN, GPIO.OUT)
GPIO.setup(HEATERPIN, GPIO.OUT)
GPIO.output(FANPIN, GPIO.LOW)
GPIO.output(HEATERPIN, GPIO.LOW)

i2c    = board.I2C()
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
bme280.sea_level_pressure = 1013.25

state_lock = threading.Lock()  # FIX 4: protect shared state
app_state = {
    'current_temp': 0.0,
    'target_temp':  25.0,
    'mode':         'manual',
    'heater_on':    False,
    'fan_on':       False
}

def control_loop():
    while True:
        try:
            temp = round(bme280.temperature, 2)
            with state_lock:
                app_state['current_temp'] = temp
                if app_state['mode'] == 'auto':
                    if temp < app_state['target_temp']:
                        app_state['heater_on'] = True
                        app_state['fan_on']    = True
                    else:
                        app_state['heater_on'] = False
                        app_state['fan_on']    = True
                GPIO.output(HEATERPIN, GPIO.HIGH if app_state['heater_on'] else GPIO.LOW)
                GPIO.output(FANPIN,    GPIO.HIGH if app_state['fan_on']    else GPIO.LOW)
        except Exception as e:
            print(f"Sensor error: {e}")
        time.sleep(2)

threading.Thread(target=control_loop, daemon=True).start()

@app.route('/')
def home():
    with state_lock:
        target = app_state['target_temp']  # FIX 3: pass variable to template
    return render_template('dashboard.html', target_temp=target)

@app.route('/api/state')
def get_state():
    with state_lock:
        return jsonify(app_state)

@app.route('/api/set_target', methods=['POST'])
def set_target():
    with state_lock:
        app_state['target_temp'] = float(request.json['target'])
    return jsonify({'status': 'ok'})

@app.route('/api/set_mode', methods=['POST'])
def set_mode():
    with state_lock:
        app_state['mode'] = request.json['mode']
    return jsonify({'status': 'ok'})

@app.route('/api/control_device', methods=['POST'])
def control_device():
    with state_lock:
        if app_state['mode'] != 'manual':
            return jsonify({'status': 'ignored', 'reason': 'Not in manual mode'})
        data   = request.json
        device = data['device']
        state  = data['state'] == 'on'
        if device == 'fan':
            app_state['fan_on'] = state
        elif device == 'heater':
            app_state['heater_on'] = stat