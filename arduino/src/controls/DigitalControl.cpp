#include "controls/DigitalControl.h"

DigitalControl::DigitalControl(const uint8_t pin, const char *type, const char *device)
    : Control(pin, type, device) {
}

void DigitalControl::begin() {
    pinMode(pin, OUTPUT);
}

void DigitalControl::setValue(const int value) {
    digitalWrite(pin, value ? HIGH : LOW);
}
