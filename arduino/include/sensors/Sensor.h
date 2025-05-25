#pragma once

#include "controls/Control.h"

struct Sensor {
    const char *id;
    const char *label;
    const char *unit;
    Control **controls;
    const size_t controlCount;

    Sensor(const char *id_, const char *label_, const char *unit_, Control **controls_, const size_t controlCount_)
        : id(id_), label(label_), unit(unit_), controls(controls_), controlCount(controlCount_) {
    }

    virtual ~Sensor() = default;
    virtual void begin() = 0;
    virtual float read() = 0;
};
