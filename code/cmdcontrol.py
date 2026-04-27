import RPi.GPIO as GPIO
import board
import threading
import time
import csv
import os
import queue
from adafruit_bme280 import basic as adafruit_bme280

# --- Configuration ---
FANPIN = 17
HEATERPIN = 27
LOG_FILE = "sensor_data.csv"
target_temp = 25.0
running = True

# --- Queue & State Variables ---
command_queue = queue.Queue()
current_task = "Idle"
auto_paused = False
interrupt_auto = False

# --- Hardware Setup ---
GPIO.setmode(GPIO.BCM)
GPIO.setup(FANPIN, GPIO.OUT)
GPIO.setup(HEATERPIN, GPIO.OUT)
GPIO.output(FANPIN, GPIO.LOW)
GPIO.output(HEATERPIN, GPIO.LOW)

i2c = board.I2C()
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
bme280.sea_level_pressure = 1013.25

# --- Helper Functions ---
def set_target_safe(new_temp):
    global target_temp
    if new_temp > 30.0: target_temp = 30.0
    elif new_temp < 18.0: target_temp = 18.0
    else: target_temp = new_temp

def write_to_csv(data_list):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Temp_C", "Humidity_%", "Pressure_hPa", "Target_C", "Fan_Status", "Heater_Status"])
        writer.writerow(data_list)

# --- Threads ---
def log_data():
    while running:
        try:
            t, h, p = bme280.temperature, bme280.relative_humidity, bme280.pressure
            f_s = 1 if GPIO.input(FANPIN) else 0
            h_s = 1 if GPIO.input(HEATERPIN) else 0
            write_to_csv([time.strftime("%Y-%m-%d %H:%M:%S"), f"{t:.2f}", f"{h:.2f}", f"{p:.2f}", target_temp, f_s, h_s])
        except: pass # Prevent I2C glitches from crashing the logger
        time.sleep(5)

def display_status():
    global running, current_task
    print("\n--- System Online ---")
    while running:
        try:
            t = bme280.temperature
            f_s = "ON" if GPIO.input(FANPIN) else "OFF"
            h_s = "ON" if GPIO.input(HEATERPIN) else "OFF"
            next_tasks = list(command_queue.queue)[:2] 
            queue_str = " -> ".join(next_tasks) if next_tasks else "None"
            print(f"\r[TEMP: {t:.2f}°C | TGT: {target_temp}°C] [FAN: {f_s} | HEAT: {h_s}] | DOING: {current_task} | NEXT: {queue_str}      ", end="")
        except: pass
        time.sleep(2)

def mission_runner():
    global auto_paused, interrupt_auto, target_temp, current_task
    while running:
        if auto_paused or command_queue.empty():
            current_task = "Paused" if auto_paused else "Idle"
            time.sleep(0.5)
            continue
            
        task = command_queue.get()
        current_task = task
        parts = task.split()
        cmd_type = parts[0]
        
        try:
            if cmd_type == "temp":
                goal = float(parts[1])
                set_target_safe(goal)
                start_wait = time.time()
                timeout_seconds = 90 * 60 # 1.5 Hours
                
                while running and not interrupt_auto:
                    current_t = bme280.temperature
                    if abs(current_t - target_temp) < 0.5:
                        write_to_csv([f"EVENT: Reached {target_temp}C", "", "", "", "", "", ""])
                        break
                    
                    if (time.time() - start_wait) > timeout_seconds:
                        # SAFETY TRIGGER: Force heater off on timeout
                        GPIO.output(HEATERPIN, GPIO.LOW)
                        write_to_csv([f"TIMEOUT: Target {target_temp}C failed. HEATER FORCED OFF", "", "", "", "", "", ""])
                        print(f"\n[ALERT] Timeout reached. Heater forced OFF.")
                        break
                    time.sleep(1)
                    
            elif cmd_type == "time":
                seconds = int(float(parts[1]) * 60)
                for s in range(seconds):
                    if not running or interrupt_auto: break
                    while auto_paused: time.sleep(0.5)
                    time.sleep(1)
                    
            elif cmd_type == "heater":
                GPIO.output(HEATERPIN, GPIO.HIGH if parts[1] == "on" else GPIO.LOW)
            elif cmd_type == "fan":
                GPIO.output(FANPIN, GPIO.HIGH if parts[1] == "on" else GPIO.LOW)
            elif cmd_type == "line":
                write_to_csv(["-"*20, "---", "---", "---", "---", "-", "-"])
            elif cmd_type == "note":
                write_to_csv([f"NOTE: {parts[1]}", "", "", "", "", "", ""])

        except Exception as e:
            print(f"\n[ERROR] Task '{task}' failed: {e}")

        command_queue.task_done()
        if interrupt_auto: interrupt_auto = False

# --- Controller ---
threading.Thread(target=display_status, daemon=True).start()
threading.Thread(target=log_data, daemon=True).start()
threading.Thread(target=mission_runner, daemon=True).start()

try:
    while True:
        cmd = input().lower().strip()
        if not cmd: continue

        if cmd.startswith("auto"):
            auto_paused = False
            interrupt_auto = False
            raw_cmds = cmd.split()[1:]
            i = 0
            while i < len(raw_cmds):
                c = raw_cmds[i]
                if c in ["temp", "time", "heater", "fan", "note"] and i+1 < len(raw_cmds):
                    command_queue.put(f"{c} {raw_cmds[i+1]}")
                    i += 2
                elif c == "line":
                    command_queue.put("line")
                    i += 1
                else: i += 1

        elif cmd == "qdel":
            interrupt_auto = True
            with command_queue.mutex: command_queue.queue.clear()
            print("\n[SYSTEM] Queue Cleared.")
            
        elif cmd == "qpause":
            auto_paused = True

        elif cmd.startswith("target"):
            try:
                val = float(''.join(filter(lambda x: x.isdigit() or x == '.', cmd)))
                set_target_safe(val)
            except: pass

        elif cmd == "line": write_to_csv(["-"*20, "", "", "", "", "", ""])
        elif cmd.startswith("note "): write_to_csv([f"NOTE: {cmd[5:]}", "", "", "", "", "", ""])
        elif cmd in ["fan on", "fan off"]: GPIO.output(FANPIN, GPIO.HIGH if "on" in cmd else GPIO.LOW)
        elif cmd in ["heater on", "heater off"]: GPIO.output(HEATERPIN, GPIO.HIGH if "on" in cmd else GPIO.LOW)
        elif cmd == "exit":
            running = False
            break
finally:
    GPIO.cleanup()