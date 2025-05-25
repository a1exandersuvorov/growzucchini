#include <Arduino.h>
#include "config/PinConfig.h"
#include "controls/Control.h"
#include "sensors/ExhFanRPMSensor.h"
#include "sensors/SensorManager.h"

ExhFanRPMSensor::ExhFanRPMSensor(const char *id, const char *label, const char *unit, Control **controls,
                                 const size_t controlCount)
    : Sensor(id, label, unit, controls, controlCount) {
}

void ExhFanRPMSensor::begin() {
    attachInterrupt(digitalPinToInterrupt(EXH_FAN_INTERRUPT_PIN), countPulse, FALLING);
}

float ExhFanRPMSensor::read() {
    noInterrupts();
    uint16_t count = pulseCount;
    pulseCount = 0;
    interrupts();
    return count * 60 / 2.0 / SensorManager::multiplier;
}

void ExhFanRPMSensor::countPulse() {
    pulseCount++;
}
