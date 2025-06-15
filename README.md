<p align="center">
    <img src="assets/zucchini.png" alt="grow zucchini" width="180"/>
</p>

GrowZucchini is a modular automation system for indoor plant environments, built with Arduino and Python. It supports
monitoring and control of key environmental factors, including:

- Climate And Soil Moisture Control.
- Growth Condition Logging And Data Visualisation.
- Modular Architecture: Add or remove sensors/controls (e.g. alarms, lights, pumps) with minimal code changes.
- Python Control App: Communicates with Arduino, supports CLI-based manual overrides, and manages data storage.
- Dockerized Deployment: Python app and InfluxDB run in isolated containers for portability and stability.

## Project Structure

- `app/`: Python application (`growzucchini`) that communicates with embedded devices, logs data to InfluxDB, and
  controls actuators.
- `arduino/`: PlatformIO-based firmware for Arduino-compatible boards, responsible for reading sensors and receiving
  control commands.
- `Makefile`: Unification of dev commands across both environments.
