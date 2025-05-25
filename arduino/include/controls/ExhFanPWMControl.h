#pragma once

#include "Control.h"

class ExhFanPWMControl final : public Control {
public:
    ExhFanPWMControl(uint8_t pin, const char* type, const char* device);

    void begin() override;
    void setValue(int value) override;
};
