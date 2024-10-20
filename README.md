# CITS5506 Project

This project is for CITS5506 Project from Semester 2, 2024.

The project is building the smart IoT-based curtain and light. This project includes two different components
- ESP32
- Web application

## ESP32 microcontroller

ESP32 performs the following tasks

- Reads in light intensity data from the light sensor
- Controls the light bulb (on/off)
- Control the motor driver that will roll up and down the curtain

Source code for this is under /microcontroller

## Web Application

Performs the following tasks

- User dashboard that will handle requests from the user
- Stores data on the users and the log information
- Talk to the ESP32's server for forwarding the user requests

Source code for this is under /server along with information on how to run