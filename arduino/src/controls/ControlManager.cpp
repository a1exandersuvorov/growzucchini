#include "config/HardwareRegistry.h"
#include "controls/ControlManager.h"
#include "controls/ExhFanPWMControl.h"

void ControlManager::begin() {
    for (const ControlEntry *entry = HardwareRegistry::getAllControls(); entry->pin != 0; ++entry) {
        entry->control->begin();
    }
}
