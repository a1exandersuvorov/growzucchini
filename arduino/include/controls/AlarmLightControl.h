#pragma once

#include "Control.h"

class AlarmLightControl final : public Control {
public:
    AlarmLightControl(uint8_t pin, const char* type, const char* device);

    void begin() override;
    void setValue(int value) override;
};
