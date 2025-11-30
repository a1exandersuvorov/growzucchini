# Katosup 
Modular automation system for indoor plant environments, built with Arduino and Python. 

[![License: MIT](https://img.shields.io/badge/License-MIT-F2BF42.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-3872E0.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/managed_by-poetry-3872E0.svg)](https://python-poetry.org/)
[![Type Checked: mypy](https://img.shields.io/badge/type%20checked-mypy-3872E0.svg)](http://mypy-lang.org/)
[![Tests: pytest](https://img.shields.io/badge/tests-pytest-58A65D.svg)](https://pytest.org/)

[![C++](https://img.shields.io/badge/c++-arduino-2D6569.svg?logo=c%2B%2B&logoColor=white)](https://www.arduino.cc/)
[![PlatformIO](https://img.shields.io/badge/embeded_env-platformio-D57A2D.svg?logo=platformio&logoColor=%23f5822a)](https://platformio.org/)

## Features

- **Climate And Soil Moisture Control**
- **Data Logging & Visualization:** Backed by InfluxDB, enabling time-series data storage and interactive dashboard
  visualization through its built-in UI.
- **Modular Architecture:** Structured around interchangeable sensor and actuator modules (e.g., alarms, lights, pumps).
  Devices can be added or removed by plugging them into well-defined integration points, without altering the system’s
  core logic. The core of the system is generic and reusable, supporting any combination of
  devices for any purpose.
- **Python Control App:** Receives sensor data from Arduino, makes control decisions, sends commands to actuators. CLI-based
  manual override is supported.
- **Dockerized Deployment:** Python app and InfluxDB run in isolated container.

## Project Structure

- `app/`: Python application (`katosup`) that communicates with embedded devices, controls actuators, and logs data
  to InfluxDB.
- `arduino/`: PlatformIO-based firmware for Arduino-compatible boards, responsible for reading sensors and receiving
  control commands.
- `Makefile`: Unification of dev commands across both environments.

## Architectural View

<p align="center">
    <img src="doc/architecture-diagram.png" alt="architectural diagram" width="1000"/>
</p>