#include "controls/AlarmLightControl.h"

AlarmLightControl::AlarmLightControl(const uint8_t pin, const char *type, const char *device)
    : Control(pin, type, device) {
}

void AlarmLightControl::begin() {
    pinMode(pin, OUTPUT);
}

void AlarmLightControl::setValue(const int value) {
    digitalWrite(pin, value ? HIGH : LOW);
}
