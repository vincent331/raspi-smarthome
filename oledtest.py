import time
import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont

i2c = busio.I2C(board.SCL, board.SDA)

oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)
#have to double check that , sudo i2cdetect -y 1

oled.fill(0)
oled.show()

image = Image.new('1', (128, 64))
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

draw.text((0, 0), "test", font=font, fill=255)
#experiment with ts

oled.image(image)
oled.show()

print('displayed')