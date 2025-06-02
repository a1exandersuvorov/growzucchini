#pragma once

#include "DigitalControl.h"

class PowerSwitchControl final : public DigitalControl {
public:
    PowerSwitchControl(uint8_t pin, const char *type, const char *device);
};

inline PowerSwitchControl::PowerSwitchControl(const uint8_t pin, const char *type, const char *device): DigitalControl(
    pin, type, device) {
}
