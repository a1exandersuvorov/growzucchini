#include "sensors/DHTHumiditySensor.h"

DHTHumiditySensor::DHTHumiditySensor(const char *id, const char *label, const char *unit, DHTSensor *dhtSensor,
                                     Control **controls, const size_t controlCount)
    : Sensor(id, label, unit, controls, controlCount), dhtSensor(dhtSensor) {
}

void DHTHumiditySensor::begin() {
    dhtSensor->begin();
}

float DHTHumiditySensor::read() {
    return dhtSensor->readHumidity();
}
