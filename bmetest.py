import board
import time
from adafruit_bme280 import basic as adafruit_bme280

i2c = board.I2C()
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
bme280.sea_level_pressure = 1013.25

while True:
    x = bme280.temperature
    print(f'{x:.2f}')
    time.sleep(5)
