#pragma once

#include "config/HardwareRegistry.h"

class SerialHandler {
public:
    static void handleCommands();
    static void sendSensorData(const SensorEntry* sensorArray, size_t sensorCount);

private:
    static void sendError(const char* msg);
};
