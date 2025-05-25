#pragma once

#include <Arduino.h>

struct Control {
    const uint8_t pin;
    const char *type;
    const char *device;

    Control(const uint8_t pin_, const char *type_, const char *device_)
        : pin(pin_), type(type_), device(device_) {
    }

    virtual ~Control() = default;
    virtual void begin() = 0;
    virtual void setValue(int value) = 0;
};
