#include <Arduino.h>
#include <ESP8266WebServer.h>
#include <ESP8266WiFi.h>
#include <Adafruit_NeoPixel.h>

const char* ssid = ""; // Enter your SSID
const char* password = ""; // Enter your WiFi password

ESP8266WebServer server(80); // Create an instance of the web server on port 80

#define LED_PIN 2
#define NUM_LEDS 60

Adafruit_NeoPixel strip(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800); // LED

void handle_ledon() {
    Serial.println("LED ON request received.");

    for (int i = 0; i < NUM_LEDS; i++) {
        strip.setPixelColor(i, strip.Color(255, 0, 0)); // Red
    }

    strip.show();
    server.send(200, "text/plain", "LED's on");
}

void handle_ledoff() {
    Serial.println("LED OFF request received.");
    strip.clear();
    strip.show();
    
    server.send(200, "text/plain", "LED's off");
}

void chaseEffect(uint8_t r, uint8_t g, uint8_t b, int wait) {
    for (int i = 0; i < NUM_LEDS; i++) {
        strip.clear();  // Alle LEDs ausschalten
        strip.setPixelColor(i, strip.Color(r, g, b)); // Aktuelle LED einschalten
        strip.show();
        delay(wait);
    }
}

void handle_NotFound() {
    Serial.println("404: Not Found");
    server.send(404, "text/plain", "404 - Page not found");
}

void setup() {
    Serial.begin(115200);
    Serial.println("");
    Serial.println("Connecting to Wi-Fi...");

    // Connect to the Wi-Fi network
    WiFi.begin(ssid, password);

    // init LED
    strip.begin();

    // Wait until the connection is established
    while (WiFi.status() != WL_CONNECTED) {
        Serial.print(".");
        chaseEffect(255, 0, 0, 10);
    }

    strip.clear();
    strip.show();
    strip.setBrightness(50);

    Serial.println("WiFi connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());  // Print the IP address of the ESP8266

    server.on("/ledon", handle_ledon);     // Handle LED on request
    server.on("/ledoff", handle_ledoff);   // Handle LED off request
    server.onNotFound(handle_NotFound);    // Handle all other unknown routes

    server.begin();
    Serial.println("Server started.");
}

void loop() {
    server.handleClient();
}