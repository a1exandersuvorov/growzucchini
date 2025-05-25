#include "config/HardwareRegistry.h"
#include "sensors/SensorManager.h"

void SensorManager::begin() {
    for (const SensorEntry *entry = HardwareRegistry::getAllSensors(); entry->id != nullptr; ++entry) {
        entry->sensor->begin();
    }
}

unsigned long SensorManager::getInterval() const {
    return interval;
}
