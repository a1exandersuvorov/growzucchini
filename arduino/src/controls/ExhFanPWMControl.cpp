#include <Arduino.h>
#include "PWM.h"
#include "controls/ExhFanPWMControl.h"


ExhFanPWMControl::ExhFanPWMControl(const uint8_t pin, const char *type, const char *device)
    : Control(pin, type, device) {
}

void ExhFanPWMControl::begin() {
    InitTimersSafe();
    SetPinFrequencySafe(static_cast<int8_t>(pin), 25000);
    pwmWrite(pin, 0);
}

void ExhFanPWMControl::setValue(const int value) {
    pwmWrite(pin, value);
}
