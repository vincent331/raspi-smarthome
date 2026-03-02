# CLS Smart Home Tech Research Club README

Code for a Smart Home Technology Experiment, where we take two scale model houses, heat them to a set temperature, and track how the temperaure falls using a BME280. The houses have two different roofs, a flat one and a slant one, and we want to see how the difference in the area of the house will affect air flow and thus thermal dissipation. The experiment is also to be expanded into the use of fans for cooling with these house types, and hopefully a future experiment based of facade area against house area and the airflow in those cases. With funding from the Royal Society and help from an experienced architect, we are going to test out how houses can be built to accommodate smart technologies better, and learn lots along the way.














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
