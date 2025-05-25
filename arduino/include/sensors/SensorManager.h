#pragma once

#include <Arduino.h>

class SensorManager {
public:
    static constexpr uint8_t multiplier = 1;

    static void begin();
    unsigned long getInterval() const;

private:
    unsigned long interval = 1000 * multiplier;
};
