# CLS Smart Home Tech Research Club README
















--------------NOTES-----------------------------------------

Todo list:
-Flask (ALL Done!)
-Wiring
-Start a preliminary experiment!
-Work on code for auto-experiment
-Work on a description for the club for readme @Arjun
-Add an INA226 to measure energy usage - how can we minimise this?


i2c errors:

sudo raspi-config
enable interface options, then i2c
then sudo i2cdetect -y 1 (look at bme and also the oled display module)


Wiring:
GPIO -> 220ohms ---> gate
                |--> 10kohms -> gnd
Source -> gnd (const)
Drain -> Fan/Heater -
Fan/Heater + -> 5v external


VCC -> fan +
Fan - -> MOSFET Drain
MOSFET source -> GND
GPIO -> 220ohms -> MOSFET Gate
then, MOSFET Gate -> 10kohms -> gnd
if you can, use flyback diode to prevent voltage spikes:
stripe cathode -> VCC
other anode -> Fan -


VCC -> heater +
heater - -> MOSFET Drain
MOSFET Source -> GND
GPIO -> 220ohms -> MOSFET Gate
then, MOSFET Gate -> 10kohms -> gnd


BME280:
bme vcc -> 3v3 pi
bme gnd -> pi gnd
bme sda -> gpio2
bme scl -> gpio3


OLED:
oled vcc -> 3v3 pi
oled gnd -> pi gnd
oled sda -> gpio2
oled scl -> gpio3


Quick Notes:
-