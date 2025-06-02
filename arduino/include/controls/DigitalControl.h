#pragma once

#include "Control.h"

class DigitalControl : public Control {
public:
    DigitalControl(uint8_t pin, const char *type, const char *device);

    void begin() override;
    void setValue(int value) override;
};
