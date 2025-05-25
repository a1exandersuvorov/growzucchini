#include <Arduino.h>
#include <ArduinoJson.h>
#include "config/HardwareRegistry.h"
#include "../../include/communication/SerialHandler.h"

void SerialHandler::handleCommands() {
    if (!Serial.available()) return;
    String input = Serial.readStringUntil('\n');
    JsonDocument doc;
    const DeserializationError err = deserializeJson(doc, input);
    if (err) return sendError(err.c_str());

    const char *cmd = doc["command"];
    const int pin = doc["pin"] | -1;
    const int value = doc["value"] | -1;
    if (!cmd || pin < 0 || value < 0) return sendError("Missing fields");

    Control *ctrl = HardwareRegistry::getControlByPin(pin);
    if (!ctrl) return sendError("No control for pin");
    ctrl->setValue(value);
}

void SerialHandler::sendSensorData(const SensorEntry *sensorArray, const size_t sensorCount) {
    for (size_t i = 0; i < sensorCount; ++i) {
        JsonDocument doc;
        doc["sensor"] = sensorArray[i].sensor->id;
        doc["label"] = sensorArray[i].sensor->label;
        doc["value"] = sensorArray[i].sensor->read();
        doc["unit"] = sensorArray[i].sensor->unit;
        const auto controls = sensorArray[i].sensor->controls;
        const size_t control_count = sensorArray[i].sensor->controlCount;
        auto ctrlArray = doc["controls"].to<JsonArray>();
        for (size_t j = 0; j < control_count; ++j) {
            auto ctrl = ctrlArray.add<JsonObject>();
            ctrl["pin"] = controls[j]->pin;
            ctrl["type"] = controls[j]->type;
            ctrl["device"] = controls[j]->device;
        }
        serializeJson(doc, Serial);
        Serial.println();
    }
}

void SerialHandler::sendError(const char *msg) {
    JsonDocument doc;
    doc["sensor"] = "error";
    doc["value"] = msg;
    serializeJson(doc, Serial);
    Serial.println();
}
