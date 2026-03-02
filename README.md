# raspi-smarthome
Smart home technology club readme

Todo list:
-Flask (ALL Done!)
-Wiring

use hostname -I
then http://ip:5000 -> has to use same wifi so no ethernet


i2c errors:

sudo raspi-config
enable interface options, then i2c
then sudo i2cdetect -y 1 (0x76, 0x77?)


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



