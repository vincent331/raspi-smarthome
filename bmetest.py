import time
import board
import busio
import adafruit_bme280

i2c = busio.I2C(board.SCL, board.SDA)

bme = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
#have to double check with sudo i2cdetect -y 1

while True:
    print('temp' % bme.temperature)
    print('humidity' % bme.humidity)
    print('pressure' % bme.pressure)
    print('---------------------')
    time.sleep(3)
    