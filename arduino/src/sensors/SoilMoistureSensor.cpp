#include "config/PinConfig.h"
#include "sensors/SoilMoistureSensor.h"

SoilMoistureSensor::SoilMoistureSensor(const char *id, const char *label, const char *unit, Control **controls,
                                       const size_t controlCount): Sensor(id, label, unit, controls, controlCount) {
}

void SoilMoistureSensor::begin() {
    // Nope
}

float SoilMoistureSensor::read() {
    return analogRead(SOIL_MOISTURE_PIN);
}
