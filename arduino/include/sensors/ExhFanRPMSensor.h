#pragma once

#include "Sensor.h"
#include "controls/Control.h"

static volatile uint16_t pulseCount = 0;

class ExhFanRPMSensor final : public Sensor {
public:
    ExhFanRPMSensor(const char *id, const char *label, const char *unit, Control **controls, size_t controlCount);

    void begin() override;
    float read() override;
    static void countPulse();
};
