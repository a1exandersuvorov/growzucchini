#pragma once

#include "DigitalControl.h"

class AlarmLightControl final : public DigitalControl {
public:
    AlarmLightControl(uint8_t pin, const char *type, const char *device);
};

inline AlarmLightControl::AlarmLightControl(const uint8_t pin, const char *type, const char *device): DigitalControl(
    pin, type, device) {
}
