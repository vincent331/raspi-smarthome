# CLS Smart Home Tech Research Club README
> Please read this document before reading our other reserach documents

## About Us
Hi. We are students based in London in the UK. Our goal is to create the ultimate smart home by experimenting with house shape, different algorithms etc to create an ultimate smart home which uses the least energy as possible while heating or cooling the house.

## What we will be varying:
- Roof shape
- Type of insulation
- The effects of having a roof/doors/windows/walls
- Floor heating vs traditional heating
- PWM cooling algorithms for fans
- Location of furniture

## Roof shape experiment

| Roof shape | Our findings |
|------------|--------------|
| [Flat roof experiment](https://github.com/vincent331/raspi-smarthome/blob/main/experiments/Flatroof.md) | - Adding airflow into a roof, such as using a fan **significantly** increases the rate of temperature increase in a house |
| [No roof experiment](https://github.com/vincent331/raspi-smarthome/blob/main/experiments/Noroof.md) | - Without a roof, warm air escapes the house at a **outstanding** rate, leading to slower heating and faster heat loss |


## Our code

| Name | Description |
|------|-------------|
| [bmetest](bmetest.py) | A program for quickly diagnosing the bme280 sensor which we use to record the temperature. |
