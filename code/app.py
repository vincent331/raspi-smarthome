from datetime import datetime, timezone
import logging
import math
import threading
import time

from flask import Flask, jsonify, request

try:
    import RPi.GPIO as GPIO
    GPIO_IMPORT_ERROR = None
except Exception as exc:
    GPIO = None
    GPIO_IMPORT_ERROR = f"RPi.GPIO import failed: {exc}"

try:
    import board
    from adafruit_bme280 import basic as adafruit_bme280
    SENSOR_IMPORT_ERROR = None
except Exception as exc:
    board = None
    adafruit_bme280 = None
    SENSOR_IMPORT_ERROR = f"BME280 import failed: {exc}"


app = Flask(__name__)
app.logger.setLevel(logging.INFO)

FANPIN = 17
HEATERPIN = 27
SENSOR_ADDRESS = 0x76
SEA_LEVEL_PRESSURE_HPA = 1013.25
CONTROL_INTERVAL_SECONDS = 2
TEMP_DEADBAND_C = 0.5

state_lock = threading.Lock()
bme280 = None

app_state = {
    "current_temp": None,
    "target_temp": 25.0,
    "mode": "manual",
    "heater_on": False,
    "fan_on": False,
    "gpio_ready": False,
    "sensor_ready": False,
    "hardware_ready": False,
    "last_sensor_error": None,
    "last_gpio_error": None,
    "last_updated": None,
}


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()


def update_hardware_ready_locked():
    app_state["hardware_ready"] = app_state["gpio_ready"] and app_state["sensor_ready"]


def mark_gpio_ready_locked():
    app_state["gpio_ready"] = True
    app_state["last_gpio_error"] = None
    update_hardware_ready_locked()


def mark_sensor_ready_locked():
    app_state["sensor_ready"] = True
    app_state["last_sensor_error"] = None
    update_hardware_ready_locked()


def mark_gpio_error_locked(message):
    app_state["gpio_ready"] = False
    app_state["last_gpio_error"] = message
    update_hardware_ready_locked()


def mark_sensor_error_locked(message):
    app_state["sensor_ready"] = False
    app_state["last_sensor_error"] = message
    update_hardware_ready_locked()


def safe_shutdown_outputs_locked():
    app_state["heater_on"] = False
    app_state["fan_on"] = False
    if GPIO is None or not app_state["gpio_ready"]:
        return
    try:
        GPIO.output(HEATERPIN, GPIO.LOW)
        GPIO.output(FANPIN, GPIO.LOW)
    except Exception as exc:
        app.logger.exception("Failed to drive GPIO low during safe shutdown")
        mark_gpio_error_locked(f"GPIO shutdown failed: {exc}")


def apply_outputs_locked():
    if GPIO is None or not app_state["gpio_ready"]:
        return False
    try:
        GPIO.output(HEATERPIN, GPIO.HIGH if app_state["heater_on"] else GPIO.LOW)
        GPIO.output(FANPIN, GPIO.HIGH if app_state["fan_on"] else GPIO.LOW)
        return True
    except Exception as exc:
        app.logger.exception("GPIO write failed")
        app_state["heater_on"] = False
        app_state["fan_on"] = False
        mark_gpio_error_locked(f"GPIO write failed: {exc}")
        return False


def setup_gpio():
    if GPIO is None:
        with state_lock:
            mark_gpio_error_locked(GPIO_IMPORT_ERROR or "RPi.GPIO is unavailable.")
        return False

    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(FANPIN, GPIO.OUT)
        GPIO.setup(HEATERPIN, GPIO.OUT)
        GPIO.output(FANPIN, GPIO.LOW)
        GPIO.output(HEATERPIN, GPIO.LOW)
    except Exception as exc:
        with state_lock:
            mark_gpio_error_locked(f"GPIO setup failed: {exc}")
        return False

    with state_lock:
        mark_gpio_ready_locked()
    return True


def setup_sensor():
    global bme280

    if board is None or adafruit_bme280 is None:
        with state_lock:
            mark_sensor_error_locked(SENSOR_IMPORT_ERROR or "BME280 libraries are unavailable.")
        return False

    try:
        i2c = board.I2C()
        sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=SENSOR_ADDRESS)
        sensor.sea_level_pressure = SEA_LEVEL_PRESSURE_HPA
    except Exception as exc:
        with state_lock:
            mark_sensor_error_locked(
                f"BME280 setup failed at I2C address 0x{SENSOR_ADDRESS:02x}: {exc}"
            )
        bme280 = None
        return False

    bme280 = sensor
    with state_lock:
        mark_sensor_ready_locked()
    return True


def update_auto_outputs_locked(temp):
    target = app_state["target_temp"]
    if temp <= target - TEMP_DEADBAND_C:
        app_state["heater_on"] = True
    elif temp >= target + TEMP_DEADBAND_C:
        app_state["heater_on"] = False

    # Keep the fan running whenever auto mode is active.
    app_state["fan_on"] = True


def error_response(status_code, message, **extra):
    payload = {"status": "error", "error": message}
    payload.update(extra)
    return jsonify(payload), status_code


def parse_json_body():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, error_response(400, "Request body must be valid JSON.")
    return data, None


def parse_on_off(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"on", "true", "1"}:
            return True
        if lowered in {"off", "false", "0"}:
            return False
    raise ValueError("state must be one of: true, false, 'on', or 'off'")


def control_loop():
    global bme280

    while True:
        if not app_state["gpio_ready"]:
            setup_gpio()
        if bme280 is None:
            setup_sensor()

        try:
            if bme280 is None:
                raise RuntimeError("BME280 sensor is unavailable.")

            temp = round(bme280.temperature, 2)

            with state_lock:
                app_state["current_temp"] = temp
                app_state["last_updated"] = utc_now_iso()
                mark_sensor_ready_locked()

                if app_state["mode"] == "auto":
                    update_auto_outputs_locked(temp)

                if not apply_outputs_locked():
                    mark_gpio_error_locked(
                        app_state["last_gpio_error"] or "GPIO output update failed."
                    )
        except Exception as exc:
            app.logger.exception("Control loop error")
            bme280 = None
            with state_lock:
                app_state["current_temp"] = None
                mark_sensor_error_locked(f"Sensor read failed: {exc}")
                safe_shutdown_outputs_locked()

        time.sleep(CONTROL_INTERVAL_SECONDS)


@app.route("/")
def home():
    return jsonify(
        {
            "service": "lab-control",
            "message": "HTML dashboard removed. Use the JSON API endpoints instead.",
            "endpoints": {
                "state": "/api/state",
                "set_target": "/api/set_target",
                "set_mode": "/api/set_mode",
                "control_device": "/api/control_device",
            },
        }
    )


@app.route("/api/state")
def get_state():
    with state_lock:
        return jsonify(dict(app_state))


@app.route("/api/set_target", methods=["POST"])
def set_target():
    data, error = parse_json_body()
    if error:
        return error

    if "target" not in data:
        return error_response(400, "Missing required field: target")

    try:
        target = float(data["target"])
    except (TypeError, ValueError):
        return error_response(400, "target must be a number.")

    if not math.isfinite(target):
        return error_response(400, "target must be a finite number.")

    with state_lock:
        app_state["target_temp"] = target

    return jsonify({"status": "ok", "target_temp": target})


@app.route("/api/set_mode", methods=["POST"])
def set_mode():
    data, error = parse_json_body()
    if error:
        return error

    mode = data.get("mode")
    if mode not in {"manual", "auto"}:
        return error_response(400, "mode must be either 'manual' or 'auto'.")

    with state_lock:
        app_state["mode"] = mode

        if mode == "auto":
            if app_state["current_temp"] is None:
                safe_shutdown_outputs_locked()
                return (
                    jsonify(
                        {
                            "status": "warning",
                            "mode": mode,
                            "message": "Mode set to auto, but no sensor reading is available yet. Outputs are off until the sensor recovers.",
                        }
                    ),
                    503,
                )
            update_auto_outputs_locked(app_state["current_temp"])

        applied = apply_outputs_locked()
        if not applied and app_state["gpio_ready"] is False:
            return (
                jsonify(
                    {
                        "status": "warning",
                        "mode": mode,
                        "message": "Mode updated, but GPIO is unavailable so the hardware state could not be applied.",
                        "gpio_error": app_state["last_gpio_error"],
                    }
                ),
                503,
            )

    return jsonify({"status": "ok", "mode": mode})


@app.route("/api/control_device", methods=["POST"])
def control_device():
    data, error = parse_json_body()
    if error:
        return error

    with state_lock:
        if app_state["mode"] != "manual":
            return error_response(
                409,
                "Manual device control is only allowed in manual mode.",
                mode=app_state["mode"],
            )

    device = data.get("device")
    if device not in {"fan", "heater"}:
        return error_response(400, "device must be either 'fan' or 'heater'.")

    if "state" not in data:
        return error_response(400, "Missing required field: state")

    try:
        desired_state = parse_on_off(data["state"])
    except ValueError as exc:
        return error_response(400, str(exc))

    with state_lock:
        if device == "fan":
            app_state["fan_on"] = desired_state
        else:
            app_state["heater_on"] = desired_state

        applied = apply_outputs_locked()
        if not applied:
            return (
                jsonify(
                    {
                        "status": "warning",
                        "device": device,
                        "desired_state": desired_state,
                        "message": "State was updated in memory, but GPIO is unavailable so the hardware may not have changed.",
                        "gpio_error": app_state["last_gpio_error"],
                    }
                ),
                503,
            )

    return jsonify({"status": "ok", "device": device, "state": desired_state})


@app.errorhandler(404)
def handle_404(_error):
    return error_response(
        404,
        "Unknown endpoint. Use '/', '/api/state', '/api/set_target', '/api/set_mode', or '/api/control_device'.",
    )


@app.errorhandler(405)
def handle_405(_error):
    return error_response(405, "Method not allowed for this endpoint.")


@app.errorhandler(500)
def handle_500(error):
    app.logger.exception("Unhandled server error: %s", error)
    return error_response(500, "Unexpected server error.")


setup_gpio()
setup_sensor()
threading.Thread(target=control_loop, daemon=True, name="control-loop").start()


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
    finally:
        with state_lock:
            safe_shutdown_outputs_locked()

        if GPIO is not None:
            try:
                GPIO.cleanup()
            except Exception as exc:
                app.logger.exception("GPIO cleanup failed: %s", exc)
