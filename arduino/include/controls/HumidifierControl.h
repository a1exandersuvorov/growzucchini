#pragma once

#include "DigitalControl.h"

class HumidifierControl final : public DigitalControl {
public:
    HumidifierControl(uint8_t pin, const char *type, const char *device);
};

inline HumidifierControl::HumidifierControl(const uint8_t pin, const char *type, const char *device): DigitalControl(
    pin, type, device) {
}
