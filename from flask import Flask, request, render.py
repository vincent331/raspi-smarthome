from flask import Flask, request, render_template, jsonify
import RPi.GPIO as GPIO
import board
import busio
import adafruit_bme280
import threading
import time
from sklearn.neural_network import MLPRegressor  # ignore for now
import csv
import os
import pickle
import numpy as np
from sklearn.preprocessing import LabelEncoder  # ignore for now
import tkinter as tk
from tkinter import ttk


if not os.path.exists('experimentdata123.csv'):
    with open('experimentdata123.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'temp1', 'temp2',
                         'heater1', 'heater2', 'fan1', 'fan2',
                         'target_temp1', 'target_temp2',
                         'target_time1', 'target_time2'])


FANPIN1, FANPIN2       = 17, 18
HEATERPIN1, HEATERPIN2 = 27, 28

GPIO.setmode(GPIO.BCM)
for pin in [FANPIN1, FANPIN2, HEATERPIN1, HEATERPIN2]:
    GPIO.setup(pin, GPIO.OUT)

fanpwm1 = GPIO.PWM(FANPIN1, 1000); fanpwm1.start(0)
fanpwm2 = GPIO.PWM(FANPIN2, 1000); fanpwm2.start(0)
GPIO.output(HEATERPIN1, GPIO.LOW)
GPIO.output(HEATERPIN2, GPIO.LOW)

i2c  = board.I2C()
bme1 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
bme2 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x77)


state = {
    'heater1': 0, 'heater2': 0,
    'fan1': 0.0,  'fan2': 0.0,
    'target_temp1': None, 'target_temp2': None,
    'target_time1': None, 'target_time2': None,#seconds remaining
}
state_lock = threading.Lock()

def logging_loop():
    while True:
        temp1 = bme1.temperature
        temp2 = bme2.temperature
        with state_lock:
            row = [
                time.strftime('%Y-%m-%d %H:%M:%S'),
                round(temp1, 2), round(temp2, 2),
                state['heater1'], state['heater2'],
                state['fan1'],    state['fan2'],
                state['target_temp1'], state['target_temp2'],
                state['target_time1'], state['target_time2'],
            ]
        with open('experimentdata123.csv', 'a', newline='') as f:
            csv.writer(f).writerow(row)
        time.sleep(5)

threading.Thread(target=logging_loop, daemon=True).start()

def automation_loop():
    while True:
        temp1 = bme1.temperature
        temp2 = bme2.temperature

        with state_lock:
            for temp, heater_key, pin in [
                (temp1, 'target_temp1', HEATERPIN1),
                (temp2, 'target_temp2', HEATERPIN2),
            ]:
                target = state[heater_key]
                if target is not None and temp >= target:
                    GPIO.output(pin, GPIO.LOW)
                    heater_state_key = heater_key.replace('target_temp', 'heater')
                    state[heater_state_key] = 0
                    state[heater_key] = None#clear target

            for time_key, heater_key, fan_key, hpin, fpwm in [
                ('target_time1', 'heater1', 'fan1', HEATERPIN1, fanpwm1),
                ('target_time2', 'heater2', 'fan2', HEATERPIN2, fanpwm2),
            ]:
                if state[time_key] is not None:
                    state[time_key] -= 1
                    if state[time_key] <= 0:
                        GPIO.output(hpin, GPIO.LOW)
                        fpwm.ChangeDutyCycle(0)
                        state[heater_key] = 0
                        state[fan_key]    = 0.0
                        state[time_key]   = None

        time.sleep(1)

threading.Thread(target=automation_loop, daemon=True).start()

root = tk.Tk()
root.title("House Experiment Controller")
root.resizable(False, False)

# helper
def section(parent, title):
    f = tk.LabelFrame(parent, text=title, padx=8, pady=6)
    f.pack(fill='x', padx=10, pady=4)
    return f

read_frame = section(root, "Live Temperatures")
lbl_t1 = tk.Label(read_frame, text="House 1: --°C", font=("Arial", 14))
lbl_t1.grid(row=0, column=0, padx=20)
lbl_t2 = tk.Label(read_frame, text="House 2: --°C", font=("Arial", 14))
lbl_t2.grid(row=0, column=1, padx=20)

def refresh_temps():
    try:
        lbl_t1.config(text=f"House 1: {bme1.temperature:.1f}°C")
        lbl_t2.config(text=f"House 2: {bme2.temperature:.1f}°C")
    except Exception:
        pass
    root.after(1000, refresh_temps)

ctrl_frame = section(root, "Manual Controls")

def toggle_heater(pin, key, var):
    val = var.get()
    GPIO.output(pin, GPIO.HIGH if val else GPIO.LOW)
    with state_lock:
        state[key] = int(val)

def update_fan(pwm, key, val):
    duty = float(val)
    pwm.ChangeDutyCycle(duty)
    with state_lock:
        state[key] = duty

h1_var = tk.BooleanVar()
h2_var = tk.BooleanVar()

tk.Label(ctrl_frame, text="House 1").grid(row=0, column=0)
tk.Checkbutton(ctrl_frame, text="Heater", variable=h1_var,
               command=lambda: toggle_heater(HEATERPIN1, 'heater1', h1_var)).grid(row=1, column=0)
tk.Label(ctrl_frame, text="Fan").grid(row=2, column=0)
fan1_var = tk.DoubleVar()
tk.Scale(ctrl_frame, variable=fan1_var, from_=0, to=100, orient=tk.HORIZONTAL, length=150,
         command=lambda v: update_fan(fanpwm1, 'fan1', v)).grid(row=3, column=0, padx=10)

tk.Label(ctrl_frame, text="House 2").grid(row=0, column=1)
tk.Checkbutton(ctrl_frame, text="Heater", variable=h2_var,
               command=lambda: toggle_heater(HEATERPIN2, 'heater2', h2_var)).grid(row=1, column=1)
tk.Label(ctrl_frame, text="Fan").grid(row=2, column=1)
fan2_var = tk.DoubleVar()
tk.Scale(ctrl_frame, variable=fan2_var, from_=0, to=100, orient=tk.HORIZONTAL, length=150,
         command=lambda v: update_fan(fanpwm2, 'fan2', v)).grid(row=3, column=1, padx=10)


temp_frame = section(root, "Target Temp Mode (heater auto-off when reached)")

def start_target_temp(heater_key, pin, entry, h_var):
    try:
        target = float(entry.get())
    except ValueError:
        return
    GPIO.output(pin, GPIO.HIGH)
    h_var.set(True)
    with state_lock:
        state[heater_key.replace('target_temp', 'heater')] = 1
        state[heater_key] = target

for col, (tk_key, pin, entry_hint, h_var_ref) in enumerate([
    ('target_temp1', HEATERPIN1, "e.g. 30", 'h1_var'),
    ('target_temp2', HEATERPIN2, "e.g. 30", 'h2_var'),
]):
    tk.Label(temp_frame, text=f"House {col+1} target (°C)").grid(row=0, column=col, padx=10)

h1_temp_entry = tk.Entry(temp_frame, width=8); h1_temp_entry.grid(row=1, column=0)
h2_temp_entry = tk.Entry(temp_frame, width=8); h2_temp_entry.grid(row=1, column=1)
tk.Button(temp_frame, text="Start H1",
          command=lambda: start_target_temp('target_temp1', HEATERPIN1, h1_temp_entry, h1_var)).grid(row=2, column=0, pady=4)
tk.Button(temp_frame, text="Start H2",
          command=lambda: start_target_temp('target_temp2', HEATERPIN2, h2_temp_entry, h2_var)).grid(row=2, column=1, pady=4)


time_frame = section(root, "Target Time Mode (heater+fan auto-off after duration)")

def start_target_time(time_key, heater_key, fan_key, hpin, fpwm, entry, h_var, fan_var):
    try:
        seconds = int(float(entry.get()) * 60)#entry in minutes
    except ValueError:
        return
    GPIO.output(hpin, GPIO.HIGH)
    duty = fan_var.get()
    fpwm.ChangeDutyCycle(duty)
    h_var.set(True)
    with state_lock:
        state[heater_key] = 1
        state[fan_key]    = duty
        state[time_key]   = seconds

tk.Label(time_frame, text="House 1 duration (min)").grid(row=0, column=0, padx=10)
tk.Label(time_frame, text="House 2 duration (min)").grid(row=0, column=1, padx=10)
h1_time_entry = tk.Entry(time_frame, width=8); h1_time_entry.grid(row=1, column=0)
h2_time_entry = tk.Entry(time_frame, width=8); h2_time_entry.grid(row=1, column=1)
tk.Button(time_frame, text="Start H1",
          command=lambda: start_target_time('target_time1','heater1','fan1',
                                            HEATERPIN1, fanpwm1, h1_time_entry, h1_var, fan1_var)).grid(row=2, column=0, pady=4)
tk.Button(time_frame, text="Start H2",
          command=lambda: start_target_time('target_time2','heater2','fan2',
                                            HEATERPIN2, fanpwm2, h2_time_entry, h2_var, fan2_var)).grid(row=2, column=1, pady=4)


lbl_cd1 = tk.Label(time_frame, text=""); lbl_cd1.grid(row=3, column=0)
lbl_cd2 = tk.Label(time_frame, text=""); lbl_cd2.grid(row=3, column=1)

def refresh_countdowns():
    with state_lock:
        t1 = state['target_time1']
        t2 = state['target_time2']
    lbl_cd1.config(text=f"{t1}s left" if t1 is not None else "")
    lbl_cd2.config(text=f"{t2}s left" if t2 is not None else "")
    root.after(1000, refresh_countdowns)

def on_close():
    GPIO.cleanup()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
refresh_temps()
refresh_countdowns()
root.mainloop()