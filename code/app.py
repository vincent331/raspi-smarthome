from flask import Flask, request, render_template, jsonify
import RPi.GPIO as GPIO
import board
import threading
import time

#from the original bme280.py
from adafruit_bme280 import basic as adafruit_bme280

app = Flask(__name__)

#pins, I think we should def check this ---------------------------------------
FANPIN = 17
HEATERPIN = 27

#gpio stuff
GPIO.setmode(GPIO.BCM)
GPIO.setup(FANPIN, GPIO.OUT)
GPIO.setup(HEATERPIN, GPIO.OUT)
GPIO.output(FANPIN, GPIO.LOW)
GPIO.output(HEATERPIN, GPIO.LOW)

#bme setup from the original bme280.py
i2c = board.I2C()
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
bme280.sea_level_pressure = 1013.25

#fake, manafactured starting data
app_state = {
    'current_temp': 0.0,
    'target_temp': 25.0,
    'mode': 'manual', #auto or manual
    'heater_on': False,
    'fan_on': False
}

def control_algorithm():
    """Background thread that runs the temp control logic continuously (really tuff)"""
    while True:
        try:
            #const read current temp
            app_state['current_temp'] = round(bme280.temperature, 2)

            #if auto, do logic (if high, heater on), (if low, heater off)
            if app_state['mode'] == 'auto':
                if app_state['current_temp'] < app_state['target_temp']:
                    app_state['heater_on'] = True
                    app_state['fan_on'] = True #fan will actually be on to help circulation
                else:
                    app_state['heater_on'] = False
                    app_state['fan_on'] = True #fan on to cool

            #do stuff to hardware
            GPIO.output(HEATERPIN, GPIO.HIGH if app_state['heater_on'] else GPIO.LOW)
            GPIO.output(FANPIN, GPIO.HIGH if app_state['fan_on'] else GPIO.LOW)

        except Exception as e:
            print(f"Sensor error: {e}")
        
        #2 secs should be fine?
        time.sleep(2)

#start the background algorithm thread
thread = threading.Thread(target=control_algorithm, daemon=True)
thread.start()

@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/api/state')
def get_state():
    #return EVERYTHING to display stuff
    return jsonify(app_state)

@app.route('/api/set_target', methods=['POST'])
def set_target():
    data = request.json
    app_state['target_temp'] = float(data['target'])
    return jsonify({'status': 'ok'})

@app.route('/api/set_mode', methods=['POST'])
def set_mode():
    data = request.json
    app_state['mode'] = data['mode']
    return jsonify({'status': 'ok'})

@app.route('/api/control_device', methods=['POST'])
def control_device():
    #ONLY MANUAL IF IN MANUAL - IMPORTANT
    if app_state['mode'] == 'manual':
        data = request.json
        device = data['device']
        state = data['state'] == 'on'
        
        if device == 'fan':
            app_state['fan_on'] = state
        elif device == 'heater':
            app_state['heater_on'] = state
            
        return jsonify({'status': 'ok'})
    return jsonify({'status': 'ignored', 'reason': 'System is in Auto mode'})

if __name__ == "__main__":
    try:
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    finally:
        GPIO.cleanup() #ofc we do ts