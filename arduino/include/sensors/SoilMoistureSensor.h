#pragma once

#include "Sensor.h"

class SoilMoistureSensor final : public Sensor {
public:
    SoilMoistureSensor(const char *id, const char *label, const char *unit, Control **controls, size_t controlCount);

    void begin() override;
    float read() override;
};
