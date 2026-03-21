# CLS Smart Home Tech Research Club README
> Please read this document before reading our other research documents

## About Us
Hi. We are students based in London in the UK. Our goal is to experiment with house shape, different algorithms, roof type, etc to create an ideal smart home which uses the least energy as possible while heating or cooling the house.

## Main Experimenting
- We will primarily be experimenting how the roof pitch (the angle between the sloped part and the base) affects rate of temperature change. Many papers and articles have been written in the past showing how this works, but with limitations such as the location. Not many have tested roof pitch with a real model at all, and also not in UK conditions.
- Our hypothesis is that the flat roof model will heat the fastest due to the smaller volume of air that needs to be heated. 

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
| [No roof experiment](https://github.com/vincent331/raspi-smarthome/blob/main/experiments/Noroof.md) | - Without a roof, warm air escapes the house at a **outstanding** rate, leading to slower heating and faster heat loss - we used this as our control |


## Our code

| Name | Description |
|------|-------------|
| [bmetest](bmetest.py) | A program for quickly diagnosing the bme280 sensor which we use to record the temperature. |
