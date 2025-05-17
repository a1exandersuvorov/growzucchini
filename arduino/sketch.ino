#include <ArduinoJson.h>
#include <DHT.h>

// ==== CONFIGURATION ====
#define EXH_FAN_INTERRUPT_PIN 2
#define EXH_FAN_CONTROL_PIN 3  // PWM 490 Hz
#define ALARM_LIGHT_PIN 4
#define BUZZER_PIN 5
#define DHTPIN 7
#define DHTTYPE DHT11

#define ARRAY_SIZE(arr) (sizeof(arr) / sizeof((arr)[0]))

DHT dht(DHTPIN, DHTTYPE);

uint8_t intervalMultiplier = 5;

volatile uint16_t exhFanTachCounter = 0;

void countExhFanTachPulse() {
  exhFanTachCounter++;
}

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

float readExhFanRPM() {
  noInterrupts();
  uint16_t count = exhFanTachCounter;
  exhFanTachCounter = 0;
  interrupts();
  return (count * 60.0) / 2.0 / intervalMultiplier;  // 2 pulses per revolution;
}

// === Control objects ===
Control alarmLight = {ALARM_LIGHT_PIN, "digital", "alarm_light"};
Control exhaustFan = {EXH_FAN_CONTROL_PIN, "analog", "exhaust_fan"};

Control tempControls[] = {exhaustFan};
Control humidityControls[] = {alarmLight};
Control exhFanSpeedControls[] = {exhaustFan};

// Control smokeControls[] = {
//   {ALARM_LIGHT_PIN, "digital", "alarm_light"},
//   {BUZZER_PIN, "digital", "alarm_sound"}
// };

// Control moistureControls[] = {
//   {PUMP_PIN, "digital", "irrigate"}
// };

// === Sensor config ===
Sensor sensors[] = {
  {"dt", "Temperature", "C", readTemperature, tempControls, ARRAY_SIZE(tempControls)},
  {"dh", "Humidity", "%", readHumidity, humidityControls, ARRAY_SIZE(humidityControls)},
  {"exh", "Exhaust Fan Speed", "rpm", readExhFanRPM, exhFanSpeedControls, ARRAY_SIZE(exhFanSpeedControls)}
  // {"smoke", "Smoke", "ppm", readSmoke, smokeControls, ARRAY_SIZE(smokeControls)},
  // {"moisture", "Soil Moisture", "%", readMoisture, moistureControls, ARRAY_SIZE(moistureControls)}
};

const int sensorCount = ARRAY_SIZE(sensors);
const unsigned long interval = 1000 * intervalMultiplier;
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
  attachInterrupt(digitalPinToInterrupt(EXH_FAN_INTERRUPT_PIN), countExhFanTachPulse, FALLING);
  analogWrite(EXH_FAN_CONTROL_PIN, 0);
//   delay(5000);
//   analogWrite(EXH_FAN_CONTROL_PIN, 255);
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
  doc["sensor"] = "error";
  doc["value"] = msg;
  serializeJson(doc, Serial);
  Serial.println();
}
