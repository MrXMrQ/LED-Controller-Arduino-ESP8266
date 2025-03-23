#include <Arduino.h>

void setup() {
    Serial.begin(115200);
    Serial.println("ESP8266 ist bereit!");
}

void loop() {
    Serial.println("Hallo von NodeMCU!");
    delay(1000);
}
