#include <ArduinoJson.h>
#include <DHT.h>

// ==== CONFIGURATION ====
#define DHTPIN 2
#define DHTTYPE DHT11
#define FAN_PIN 3
#define ALARM_LIGHT_PIN 4
#define PUMP_PIN 7
#define BUZZER_PIN 5

#define ARRAY_SIZE(arr) (sizeof(arr) / sizeof((arr)[0]))

DHT dht(DHTPIN, DHTTYPE);


// === Structures ===
struct Control {
  uint8_t pin;
  const char* type;           // "digital", "pwm", "analog"
  const char* device;         // "cool", "alarm", etc.
};

struct Sensor {
  const char* id;
  const char* label;
  const char* unit;
  float (*read)();
  Control* controls;
  uint8_t controlCount;
};

// === Read functions ===
float readTemperature() { return dht.readTemperature(); }
float readHumidity()    { return dht.readHumidity(); }
float readSmoke()       { return analogRead(A0); }
float readMoisture()    { return analogRead(A1); }

// === Control objects ===
// Control tempControls[] = {
//   {FAN_PIN, "pwm", "cool"}
// };

// Control humidityControls[] = {
//   {PUMP_PIN, "digital", "dry"}
// };

Control humidityControls[] = {
  {ALARM_LIGHT_PIN, "digital", "alarm_light"}
};

Control smokeControls[] = {
  {ALARM_LIGHT_PIN, "digital", "alarm_light"},
  {BUZZER_PIN, "digital", "alarm_sound"}
};

Control moistureControls[] = {
  {PUMP_PIN, "digital", "irrigate"}
};

// === Sensor config ===
Sensor sensors[] = {
  // {"dt", "Temperature", "C", readTemperature, tempControls, ARRAY_SIZE(tempControls)},
  {"dh", "Humidity", "%", readHumidity, humidityControls, ARRAY_SIZE(humidityControls)},
  // {"smoke", "Smoke", "ppm", readSmoke, smokeControls, ARRAY_SIZE(smokeControls)},
  // {"moisture", "Soil Moisture", "%", readMoisture, moistureControls, ARRAY_SIZE(moistureControls)}
};

const int sensorCount = ARRAY_SIZE(sensors);
const unsigned long interval = 5000;
unsigned long lastSend = 0;

// === Setup ===
void setup() {
  Serial.begin(9600);
  dht.begin();
  for (int i = 0; i < sensorCount; ++i) {
    for (int j = 0; j < sensors[i].controlCount; ++j) {
      pinMode(sensors[i].controls[j].pin, OUTPUT);
    }
  }
}

// === Loop ===
void loop() {
  handleSerialCommands();
  sendSensorData();
}

// === Send JSON sensor data ===
void sendSensorData() {
  unsigned long now = millis();
  if (now - lastSend < interval) return;
  lastSend = now;

  for (int i = 0; i < sensorCount; ++i) {
    float value = sensors[i].read();
    if (isnan(value)) continue;

    StaticJsonDocument<256> doc;
    doc["sensor"] = sensors[i].id;
    doc["label"] = sensors[i].label;
    doc["value"] = value;
    doc["unit"] = sensors[i].unit;

    JsonArray ctrlArray = doc.createNestedArray("controls");
    for (int j = 0; j < sensors[i].controlCount; ++j) {
      JsonObject ctrl = ctrlArray.createNestedObject();
      ctrl["pin"] = sensors[i].controls[j].pin;
      ctrl["type"] = sensors[i].controls[j].type;
      ctrl["device"] = sensors[i].controls[j].device;
    }

    serializeJson(doc, Serial);
    Serial.println(); // newline to mark end
  }
}

// === Receive and handle commands from Python ===
void handleSerialCommands() {
  if (!Serial.available()) return;

  String input = Serial.readStringUntil('\n');
  StaticJsonDocument<128> doc;
  DeserializationError err = deserializeJson(doc, input);

  if (err) {
    sendError((const char*)err.f_str());
    return;
  }

  const char* cmd = doc["command"];
  if (!cmd) {
    sendError("Missing command");
    return;
  }

  if (strcmp(cmd, "digital") == 0 || strcmp(cmd, "analog") == 0) {
    int pin = doc["pin"] | -1;
    int value = doc["value"] | -1;

    if (pin < 0 || value < 0) {
      sendError("Invalid pin or value");
      return;
    }

    if (strcmp(cmd, "digital") == 0)
      digitalWrite(pin, value ? HIGH : LOW);
    else
      analogWrite(pin, value);

  } else if (strcmp(cmd, "pin_mode") == 0) {
    int pin = doc["pin"] | -1;
    const char* mode = doc["mode"];
    if (pin < 0 || !mode) {
      sendError("Missing pin or mode");
      return;
    }

    if (strcmp(mode, "output") == 0) pinMode(pin, OUTPUT);
    else if (strcmp(mode, "input") == 0) pinMode(pin, INPUT);
    else if (strcmp(mode, "input_pullup") == 0) pinMode(pin, INPUT_PULLUP);
    else sendError("Unknown mode");

  } else {
    sendError("Unknown command");
  }
}

// === Error helper ===
void sendError(const char* msg) {
  StaticJsonDocument<128> doc;
  doc["error"] = msg;
  serializeJson(doc, Serial);
  Serial.println();
}
