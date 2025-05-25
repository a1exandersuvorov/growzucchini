#include "config/HardwareRegistry.h"
#include "config/PinConfig.h"
#include "controls/AlarmLightControl.h"
#include "controls/ExhFanPWMControl.h"
#include "sensors/DHTSensor.h"
#include "sensors/DHTHumiditySensor.h"
#include "sensors/DHTTemperatureSensor.h"
#include "sensors/ExhFanRPMSensor.h"
#include "../../lib/Util.h"

// === Control config ===
AlarmLightControl alarmLight(ALARM_LIGHT_PIN, "digital", "alarm_light");
ExhFanPWMControl exhFan(EXH_FAN_CONTROL_PIN, "analog", "exhaust_fan");

Control *temperatureControl[] = {&exhFan};
Control *humidityControl[] = {&alarmLight};
Control *exhFanRPMControl[] = {&exhFan};

// === Sensor config ===
DHTSensor dht(DHTPIN, DHTTYPE);
DHTTemperatureSensor dhtTemperature("dt", "Temperature", "C", &dht, temperatureControl, ARRAY_SIZE(temperatureControl));
DHTHumiditySensor dhtHumidity("dh", "Humidity", "%", &dht, humidityControl, ARRAY_SIZE(humidityControl));
ExhFanRPMSensor exhFanRPM("exh", "Exhaust Fan Speed", "rpm", exhFanRPMControl, ARRAY_SIZE(exhFanRPMControl));


const ControlEntry HardwareRegistry::controlArray[] = {
    {ALARM_LIGHT_PIN, &alarmLight},
    {EXH_FAN_CONTROL_PIN, &exhFan},
    {0, nullptr} // sentinel to mark end
};

const SensorEntry HardwareRegistry::sensorArray[] = {
    {"dt", &dhtTemperature},
    {"dh", &dhtHumidity},
    {"rpm", &exhFanRPM},
    {nullptr, nullptr} // sentinel to mark end
};

const ControlEntry *HardwareRegistry::getAllControls() {
    return controlArray;
}

Control *HardwareRegistry::getControlByPin(const uint8_t pin) {
    for (const ControlEntry *entry = controlArray; entry->pin != 0; ++entry) {
        if (pin == entry->pin) return entry->control;
    }
    return nullptr;
}

const SensorEntry *HardwareRegistry::getAllSensors() {
    return sensorArray;
}

constexpr size_t HardwareRegistry::sensorArraySize = ARRAY_SIZE(sensorArray);

size_t HardwareRegistry::getSensorCount() {
    return sensorArraySize - 1;
}
