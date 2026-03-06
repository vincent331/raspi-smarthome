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


TEST 1 - unfinished:
We started our first test using the house with the flat roof and all windows and doors secured with tape. Unfortunately, we could not finish the heating in the time we had, but there is a chart below to show the date we did collect.
<img width="591" height="356" alt="image" src="https://github.com/user-attachments/assets/00c35206-4ce2-40d7-9216-d77fa3e377c0" />



TEST 2 - unfinished:
Did not finish this experiment due to lack of time, this time starting from the lowest temperature and heating from there - no need for cooling the room at the start. Image below:
<img width="579" height="354" alt="image" src="https://github.com/user-attachments/assets/76c71fa9-d967-42c8-b18b-013227259105" />

TEST 3:
Ran an experiment for an hour where we heated the house to about 28 degrees then cooled it in the time we had - it did not go all the way to the starting 24.5 degrees. Graph below shows the steeper temperature decline compared to the increase in temperature. There was some inaccuracy from the door being opened sometimes and the windows having to be re-taped several times, causing some lapses which are wisible in the graph.
<img width="591" height="365" alt="image" src="https://github.com/user-attachments/assets/fb67a79f-1fcd-4a8a-896a-0aee96c270c9" />


Quick Notes:
-
