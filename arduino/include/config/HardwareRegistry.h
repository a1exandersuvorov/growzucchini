#pragma once

#include "controls/Control.h"
#include "sensors/Sensor.h"

struct ControlEntry {
    uint8_t pin;
    Control *control;
};

struct SensorEntry {
    const char *id;
    Sensor *sensor;
};

class HardwareRegistry {
public:
    static const ControlEntry* getAllControls();
    static Control *getControlByPin(uint8_t pin);

    static const SensorEntry* getAllSensors();
    static size_t getSensorCount();

private:
    static const ControlEntry controlArray[];

    static const SensorEntry sensorArray[];
    static const size_t sensorArraySize;
};
