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




27.69
27.40
27.22
27.10
26.96
26.82
26.70
26.54
26.40
26.28
26.12
26.00
25.89
25.77
25.67
25.56
25.48
25.39
25.32
25.25
25.18
25.13
25.07
25.03
24.99
24.95
24.91
24.91
24.95
24.94
24.92
24.93
24.96
25.00
25.03
25.06
25.07
25.08
25.13
25.15
25.17
25.20
25.23
25.25
25.28
25.31
25.33
25.35
25.38
25.40
25.42
25.45
25.48
25.50
25.53
25.55
25.61
25.67
25.71
25.77
25.81
25.86
25.91
25.94
25.99
26.02
26.07
26.10
26.15
26.17
26.20
26.23
26.26
26.28
26.31
26.34
26.36
26.38
26.42
26.45
26.47
26.49
26.51
26.52
26.54
26.56
26.58
26.60
26.62
This data we collected after testing out the heating and rate of heating in the room. Unfortunately, we could not finish the heating in the time we had, but there is a chart below to show the date we did collect.
<img width="586" height="357" alt="image" src="https://github.com/user-attachments/assets/3b7eed1e-69fb-4fa8-8685-0e2bbbd98a6a" />







24.65
24.67
24.69
24.75
24.79
24.83
24.87
24.92
24.95
25.00
25.05
25.08
25.12
25.17
25.21
25.26
25.30
25.34
25.39
25.42
25.48
25.51
25.56
25.61
25.65
25.69
25.71
25.75
25.79
25.83
25.87
25.90
25.94
25.98
26.01
26.04
26.07
26.11
26.15
26.18
26.21
26.26
26.28
26.32
26.35
26.37
26.41
26.45
26.48
26.50
26.54
26.57
26.59
26.62
26.65
26.68
26.70
26.72
26.75
26.78
26.81
26.83
26.86
26.88
26.91
26.92
26.96
26.98
27.00
27.02
27.04
27.06
27.08
27.10
27.12
27.15
27.17
27.18
27.20
27.22
27.24
27.26
27.26
27.28
27.30
27.32
27.35
27.36


Quick Notes:
-
