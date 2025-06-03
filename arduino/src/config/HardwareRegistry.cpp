#include "config/HardwareRegistry.h"
#include "config/PinConfig.h"
#include "controls/AlarmLightControl.h"
#include "controls/ExhFanPWMControl.h"
#include "controls/HumidifierControl.h"
#include "controls/PowerSwitchControl.h"
#include "controls/WaterPumpControl.h"
#include "sensors/DHTSensor.h"
#include "sensors/DHTHumiditySensor.h"
#include "sensors/DHTTemperatureSensor.h"
#include "sensors/ExhFanRPMSensor.h"
#include "sensors/SoilMoistureSensor.h"
#include "../../lib/Util.h"

// === Control config ===
AlarmLightControl alarmLight(ALARM_LIGHT_PIN, "digital", "alarm_light");
ExhFanPWMControl exhFan(EXH_FAN_CONTROL_PIN, "analog", "exhaust_fan");
HumidifierControl humidifier(HUMIDIFIER_PIN, "digital", "humidifier");
PowerSwitchControl powerSwitch(POWER_SWITCH_PIN, "digital", "power_switch");
WaterPumpControl waterPump(WATER_PUMP_PIN, "digital", "water_pump");

Control *temperatureControl[] = {&exhFan};
Control *humidityControl[] = {&alarmLight, &humidifier};
Control *exhFanRPMControl[] = {&exhFan};
Control *soilMoistureControl[] = {&waterPump};

// === Sensor config ===
DHTSensor dht(DHT_PIN, DHT_TYPE);
DHTTemperatureSensor dhtTemperature("dt", "Temperature", "C", &dht, temperatureControl, ARRAY_SIZE(temperatureControl));
DHTHumiditySensor dhtHumidity("dh", "Humidity", "%", &dht, humidityControl, ARRAY_SIZE(humidityControl));
ExhFanRPMSensor exhFanRPM("ef", "Exhaust Fan Speed", "rpm", exhFanRPMControl, ARRAY_SIZE(exhFanRPMControl));
SoilMoistureSensor soilMoisture("sm", "Soil Moisture", "%", soilMoistureControl, ARRAY_SIZE(soilMoistureControl));


const ControlEntry HardwareRegistry::controlArray[] = {
    {ALARM_LIGHT_PIN, &alarmLight},
    {EXH_FAN_CONTROL_PIN, &exhFan},
    {HUMIDIFIER_PIN, &humidifier},
    {POWER_SWITCH_PIN, &powerSwitch},
    {WATER_PUMP_PIN, &waterPump},
    {0, nullptr} // sentinel to mark end
};

const SensorEntry HardwareRegistry::sensorArray[] = {
    {"dt", &dhtTemperature},
    {"dh", &dhtHumidity},
    {"ef", &exhFanRPM},
    {"sm", &soilMoisture},
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
