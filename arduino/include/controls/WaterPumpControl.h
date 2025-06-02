#pragma once

#include "DigitalControl.h"

class WaterPumpControl final : public DigitalControl {
public:
    WaterPumpControl(uint8_t pin, const char *type, const char *device);
};

inline WaterPumpControl::WaterPumpControl(const uint8_t pin, const char *type, const char *device): DigitalControl(
    pin, type, device) {
}
