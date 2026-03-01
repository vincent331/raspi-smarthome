# raspi-smarthome
Smart home technology club readme

Todo list:
-Flask
-Wiring



Flask setup:

sudo apt update
sudo apt upgrade -y
sudo apt install python3 python3-pip -y
pip3 install flask
(python3 -m flask --version)
try flasktest.py

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

