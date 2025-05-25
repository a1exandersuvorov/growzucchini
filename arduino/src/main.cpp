#include <Arduino.h>
#include "config/HardwareRegistry.h"
#include "../include/communication/SerialHandler.h"
#include "../include/controls/ControlManager.h"
#include "../include/sensors/SensorManager.h"

SensorManager sensorManager;

unsigned long lastSend = 0;

void setup() {
    Serial.begin(9600);
    SensorManager::begin();
    ControlManager::begin();
}

void loop() {
    SerialHandler::handleCommands();
    const unsigned long now = millis();
    if (now - lastSend >= sensorManager.getInterval()) {
        lastSend = now;
        SerialHandler::sendSensorData(HardwareRegistry::getAllSensors(), HardwareRegistry::getSensorCount());
    }
}
