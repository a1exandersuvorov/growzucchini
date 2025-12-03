# Architecture

<p align="center">
    <img src="../assets/architecture-diagram.png" alt="architecture diagram" width="1000"/>
</p>

Katosup is built as a **modular, plug-in/plug-out automation framework**.  
It is intentionally generic and can be used for **any IoT automation purpose**, not only plant growing.

The system consists of two main components:

---

## Arduino Firmware (C++ / PlatformIO)

The Arduino side is responsible for:

- Reading sensor values  
- Sending structured JSON data to the server   
- Receiving commands  
- Controlling actuators (fans, heaters, pumps, etc.)

Internally, it is organized into three layers:

### **Core**
A fully generic mechanism that:

- Reads data from all registered sensors  
- Forwards it to the server without knowing which sensor produced it  
- Accepts commands from the server  
- Dispatches them to the appropriate control output without knowing its purpose  

The Core does **not** contain any device-specific logic.

### **Sensors**
Sensors are abstracted through a unified `Sensor` interface.

- Any new sensor type can be added by implementing this interface
- The sensor becomes available after registering it with the Core

### **Controls**
Controls are abstracted through a `Control` interface to manage actuators (digital, analog, PWM, etc.).

- Any new control type can be added by implementing `Control` interface
- Each control type is registered to make it available to the Core

> To add or remove sensors/controls, simply implement the corresponding interface and register it.  
See the [Development guide](development-guide.md) for details.

---

## Server Application (Python)

The Python server acts as the **brain** of the system. It is responsible for:

- Receiving sensor data from the Arduino  
- Applying control logic  
- Sending commands back to Arduino  
- Publishing all data to InfluxDB  

Its architecture mirrors the Arduino side and also consists of three logical layers:

### **Core**
A generic data-flow engine that:

- Listens for sensor from Arduino  
- Routes sensor data to the controllers  
- Collects resulting commands  
- Forwards it to Arduino  

The Core does not know anything about specific sensor types or controller logic.

### **Controllers**
Controllers implement behavior rules based on certain conditions like temperature or humidity

- Receive decoded sensor data
- Compute what **Action** should be applied to change current conditions
- Forwards it to one or more Devices

Controllers are fully decoupled:

- They do not know which physical sensor produced the data
- They don't know what types of devices will process the computed actions and how they will be processed

### **Devices**
Devices implements actuators logic 

- Get the action to perform
- Determine how to process the action and what command should be sent back to Arduino  
- Publish command into the message queue when needed

Devices are fully decoupled:

- They do not know which controller produced action
- They do not know how commands reach the hardware

> To add or remove controllers/devices, implement the condition/actuator logic and register it using annotations.
See the [Development guide](development-guide.md) for details.

---
### **Message Queue**
All commands from Devices are published into a message queue. The Core consumes this queue. Commands are forwarded to
Arduino.

### **InfluxDB**
All sensor data are intercepted and sent to InfluxDB. It provides time-series data storage and visualization through
its built-in UI.

---

## Extensibility

The entire system is designed around **runtime registration** of modules:

- Register new sensors  
- Register new controls  
- Register new controllers
- Register new devices  

No part of the Core logic needs modification.

> See the [Development guide](development-guide.md) for concrete examples.
