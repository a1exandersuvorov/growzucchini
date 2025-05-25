#pragma once

#include <Arduino.h>
#include <DHT.h>

class DHTSensor {
public:
    DHTSensor(uint8_t pin, uint8_t type);

    void begin();
    float readTemperature();
    float readHumidity();

private:
    DHT dht;
    bool initialized;
};
