from flask import Flask
import board
import busio
import adafruit_bme280

app = Flask(__name__)

i2c = busio.I2C(board.SCL, board.SDA)
bme = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)

@app.route('/')
def home():
    temp = bme.temperature
    humidity = bme.humidity

    return f'''
    <h1>Room Status</h1>
    <p>Temperature: {temp:.2f} °C</p>
    <p>Humidity: {humidity:.2f} %</p>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)