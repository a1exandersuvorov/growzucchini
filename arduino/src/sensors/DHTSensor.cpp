#include <Arduino.h>
#include "sensors/DHTSensor.h"

DHTSensor::DHTSensor(const uint8_t pin, const uint8_t type)
    : dht(pin, type), initialized(false) {}

void DHTSensor::begin() {
    if (!initialized) { // synchronous call
        dht.begin();
        initialized = true;
    }
}

float DHTSensor::readTemperature() {
    return dht.readTemperature();
}

float DHTSensor::readHumidity() {
    return dht.readHumidity();
}
