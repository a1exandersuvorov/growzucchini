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
- `docs/`: Project documentation.
- `Makefile`: Unification of dev commands across both environments.

## Quick Start

### Prerequisites
- Arduino UNO
- Any sensor and any actuator, for example DHT22 and LED
- Docker
- PlatformIO

### Installation

🚧 the section is under development...

> See [Setup guide](docs/setup-guide.md) for detailed instructions.

## Architecture (High-Level Overview)

<p align="center">
    <img src="assets/architecture-diagram.png" alt="architecture diagram" width="1000"/>
</p>

- Sensors on Arduino read physical data (temperature, humidity, moisture, smoke, etc.).
- Arduino encodes readings into a unified JSON message.
- Python server receives the JSON, validates it, and routes the data to registered Controllers.
- Controllers pass structured data to Devices. Controllers control certain conditions like temperature or humidity but 
devices contain actuator behavior logic.
- Devices publish commands into a message queue.
- Server Core consumes the queue and sends commands back to Arduino.
- Arduino Core receives the command and sends it to the appropriate Control (fan, light, relay, etc.).
- All sensor data is persisted to InfluxDB and visualize it through its built-in UI.
- Add/remove Sensors, Controls, Devices, Controllers → without touching the Core on either side.

This makes the system:
- Extensible
- Hardware-agnostic
- Behavior-agnostic
- Easy to integrate into any automation scenario

> See the [Architecture overview](docs/architecture-overview.md) for details.

## Development
> See [Development guide](docs/development-guide.md).

## Electric circuit
> See [Circuit and specification](docs/electrical-circuit.md).

## Assembly
> See [Assembly guide](docs/assembly-guide.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Alexander Suvorov
