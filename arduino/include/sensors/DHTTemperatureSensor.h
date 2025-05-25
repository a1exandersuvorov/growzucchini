#pragma once

#include "DHTSensor.h"
#include "Sensor.h"
#include "controls/Control.h"

class DHTTemperatureSensor final : public Sensor {
public:
    DHTTemperatureSensor(const char *id, const char *label, const char *unit, DHTSensor *dhtSensor, Control **controls,
                         size_t controlCount);

    void begin() override;

    float read() override;

private:
    DHTSensor *dhtSensor;
};
