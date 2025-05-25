#include "sensors/DHTTemperatureSensor.h"

DHTTemperatureSensor::DHTTemperatureSensor(const char *id, const char *label, const char *unit, DHTSensor *dhtSensor,
                                           Control **controls, const size_t controlCount)
    : Sensor(id, label, unit, controls, controlCount), dhtSensor(dhtSensor) {
}

void DHTTemperatureSensor::begin() {
    dhtSensor->begin();
}

float DHTTemperatureSensor::read() {
    return dhtSensor->readTemperature();
}
