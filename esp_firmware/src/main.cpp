#include <Arduino.h>
#include <ESP8266WebServer.h>
#include <ESP8266WiFi.h>
#include <Adafruit_NeoPixel.h>

const char* ssid = ""; // Enter your SSID
const char* password = ""; // Enter your WiFi password

ESP8266WebServer server(80); // Create an instance of the web server on port 80

#define LED_PIN 2
#define NUM_LEDS 60 // Enter numbers of LED's on the strip

Adafruit_NeoPixel strip(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);

// On & Off
void ledOn(uint8_t r, uint8_t g, uint8_t b, int brightness) {
    Serial.println("LED ON request received.");
    strip.setBrightness(brightness);

    for (int i = 0; i < NUM_LEDS; i++) {
        strip.setPixelColor(i, strip.Color(r, g, b)); // Red
    }

    strip.show();
    server.send(200, "text/plain", "LED's on");
}

void ledOff() {
    Serial.println("LED OFF request received.");
    strip.clear();
    strip.show();
    
    server.send(200, "text/plain", "LED's off");
}

// Animations
void runningLights(uint8_t r, uint8_t g, uint8_t b, int wait) {
    for (int i = 0; i < NUM_LEDS; i++) {
        strip.clear();
        strip.setPixelColor(i, strip.Color(r, g, b));
        strip.show();
        delay(wait);
    }
}

void breathingLight() {
    
}

void rainbowWave() {
    
}

void stroboEffect() {
    
}

void gradientEffect() {
    
}

void fireflyEffect() {
    
}

void starShopping() {
    
}

void pulseEffect() {
    
}

void lightningEffect() {
    
}

// Not found
void notFound() {
    Serial.println("404: Not Found");
    server.send(404, "text/plain", "404 - Page not found");
}

void setup() {
    Serial.begin(115200);
    Serial.println("");
    Serial.println("Connecting to Wi-Fi...");

    // Connect to the Wi-Fi network
    WiFi.begin(ssid, password);

    // init LED-strip
    strip.begin();

    // Wait until the connection is established
    while (WiFi.status() != WL_CONNECTED) {
        Serial.print(".");
        runningLights(255, 0, 0, 10);
    }

    strip.clear();
    strip.show();
    strip.setBrightness(50);

    Serial.println("WiFi connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());  // Print the IP address of the ESP8266

    // On & Off
    server.on("/ledOn", HTTP_POST, []() { // Handle LED on request
        if (server.hasArg("r") && server.hasArg("g") && server.hasArg("b") && server.hasArg("br")) {
            uint8_t r = server.arg("r").toInt();
            uint8_t g = server.arg("g").toInt();
            uint8_t b = server.arg("b").toInt();
            int brightness = server.arg("br").toInt();
            ledOn(r, g, b, brightness);

        } else {
            server.send(400, "text/plain", "Missing arguments");
        }
    });
    server.on("/ledOff", ledOff);   // Handle LED off request

    // Animations
    server.on("/runningLights", HTTP_POST, []() {

    });
    server.on("/breathingLight", HTTP_POST, []() {

    });
    server.on("/rainbowWave", HTTP_POST, []() {

    });
    server.on("/stroboEffect", HTTP_POST, []() { 

    });
    server.on("/gradientEffect", HTTP_POST, []() { 

    });
    server.on("/fireflyEffect", HTTP_POST, []() {

    });
    server.on("/starShopping", HTTP_POST, []() {

    });
    server.on("/pulseEffect", HTTP_POST, []() {

    });
    server.on("/lightningEffect", HTTP_POST, []() {
    
    });    

    // Not found
    server.onNotFound(notFound);

    server.begin();
    Serial.println("Server started.");
}

void loop() {
    server.handleClient();
}