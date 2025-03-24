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

bool animationRunning = false;
int currentAnimation = -1;

uint8_t r = 255;
uint8_t g = 0;
uint8_t b = 0;
uint8_t r1 = 255;
uint8_t g1 = 0;
uint8_t b1 = 0;
int delayTime = 10;
int brightness = 0;

// On & Off
void ledOn() {
    Serial.println("LED ON request received.");
    strip.setBrightness(brightness);

    for (int i = 0; i < NUM_LEDS; i++) {
        strip.setPixelColor(i, strip.Color(r, g, b));
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
void runningLights() {
    for (int i = 0; i < NUM_LEDS; i++) {
        strip.clear();
        strip.setPixelColor(i, strip.Color(r, g, b));
        strip.show();
        delay(delayTime);
    }
}

// Breathing Light
void breathingLight() {
    for (int i = 0; i < brightness; i++) {
        strip.fill(strip.Color(r * i / brightness, g * i / brightness, b * i / brightness), 0, NUM_LEDS);
        strip.show();
        delay(delayTime);
    }
    
    for (int i = brightness; i >= 0; i--) {
        strip.fill(strip.Color(r * i / brightness, g * i / brightness, b * i / brightness), 0, NUM_LEDS);
        strip.show();
        delay(delayTime);
    }
}

// Rainbow Wave
void rainbowWave() {
    unsigned long startTime = millis();
    while (millis() - startTime < 3 * 1000) {
      for (int i = 0; i < 256; i++) {
        for (int j = 0; j < NUM_LEDS; j++) {
          strip.setPixelColor(j, strip.ColorHSV((i * 65536 / 256) + (j * 65536 / NUM_LEDS), 255, 255));
        }
        strip.show();
        delay(3 * 1000 / 256);
      }
    }
}

// Strobo Effect
void stroboEffect() {
    for (int i = 0; i < NUM_LEDS; i++) {
        strip.setPixelColor(i, strip.Color(r, g, b));
    }
    strip.show();
    delay(delayTime);
    strip.clear();
    strip.show();
    delay(delayTime);
}

// Gradient Effect
void gradientEffect() {
    for (int i = 0; i < NUM_LEDS; i++) {
        int red = map(i, 0, NUM_LEDS, r, r1);
        int green = map(i, 0, NUM_LEDS, g, g1);
        int blue = map(i, 0, NUM_LEDS, b, b1);
        strip.setPixelColor(i, strip.Color(red, green, blue));
    }
    strip.show();
    delay(100);
}

// Firefly Effect
void fireflyEffect() {
    for (int i = 0; i < NUM_LEDS; i++) {
        if (random(0, 100) < 10) {
            strip.setPixelColor(i, strip.Color(random(0, 255), random(0, 255), random(0, 255)));
        } else {
            strip.setPixelColor(i, strip.Color(0, 0, 0));
        }
    }
    strip.show();
    delay(random(50, delayTime));
}

// Star Shopping Effect
void starShopping() {
    for (int i = 0; i < NUM_LEDS; i++) {
        if (random(0, 100) < 10) {
            strip.setPixelColor(i, strip.Color(r, g, b));
        } else {
            strip.setPixelColor(i, strip.Color(0, 0, 0));
        }
    }
    strip.show();
    delay(delayTime);
}

// Not found
void notFound() {
    Serial.println("404: Not Found");
    server.send(404, "text/plain", "404 - Page not found");
}

void runAnimation(int animationIndex) {
    switch (animationIndex) {
        case 0: runningLights(); break;
        case 1: breathingLight(); break;
        case 2: rainbowWave(); break;
        case 3: stroboEffect(); break;
        case 4: gradientEffect(); break;
        case 5: fireflyEffect(); break;
        case 6: starShopping(); break;
        default: break;
    }
}

void stopAnimation() {
    animationRunning = false;
    currentAnimation = -1;

    server.send(200, "text/plain", "Animation stopped!");
}

void startAnimation(int animationIndex) {
    if (currentAnimation == animationIndex) {
        stopAnimation();    
    }

    currentAnimation = animationIndex;
    animationRunning = true;
    server.send(200, "text/plain", "Animation started!");
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
        runningLights();
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
            r = server.arg("r").toInt();
            g = server.arg("g").toInt();
            b = server.arg("b").toInt();
            brightness = server.arg("br").toInt();
            ledOn();
        } else {
            server.send(400, "text/plain", "Missing arguments");
        }
    });

    server.on("/stop", HTTP_POST, []() {
        stopAnimation();
    });

    server.on("/ledOff", ledOff);

    // Animations
    server.on("/runningLights", HTTP_POST, []() {
        if (server.hasArg("r") && server.hasArg("g") && server.hasArg("b") && server.hasArg("d")) {
            r = server.arg("r").toInt();
            g = server.arg("g").toInt();
            b = server.arg("b").toInt();
            delayTime = server.arg("d").toInt();
            startAnimation(0);
        } else {
            server.send(400, "text/plain", "Missing arguments");
        }
    });

    server.on("/breathingLight", HTTP_POST, []() {
        if (server.hasArg("r") && server.hasArg("g") && server.hasArg("b") && server.hasArg("br") && server.hasArg("d")) {
            r = server.arg("r").toInt();
            g = server.arg("g").toInt();
            b = server.arg("b").toInt();
            brightness = server.arg("br").toInt();
            delayTime = server.arg("d").toInt();
            startAnimation(1);
        } else {
            server.send(400, "text/plain", "Missing arguments");
        }
    });

    server.on("/rainbowWave", HTTP_POST, []() {
        startAnimation(2);  
    });

    server.on("/stroboEffect", HTTP_POST, []() { 
        if (server.hasArg("r") && server.hasArg("g") && server.hasArg("b") && server.hasArg("d")) {
            r = server.arg("r").toInt();
            g = server.arg("g").toInt();
            b = server.arg("b").toInt();
            delayTime = server.arg("d").toInt();
            startAnimation(3);
        } else {
            server.send(400, "text/plain", "Missing arguments");
        }
    });

    server.on("/gradientEffect", HTTP_POST, []() { 
        if (server.hasArg("r") && server.hasArg("g") && server.hasArg("b") && server.hasArg("r1") && server.hasArg("g1") && server.hasArg("b1")) {
            r = server.arg("r").toInt();
            g = server.arg("g").toInt();
            b = server.arg("b").toInt();
            r1 = server.arg("r1").toInt();
            g1 = server.arg("g1").toInt();
            b1 = server.arg("b1").toInt();
            startAnimation(4);
        } else {
            server.send(400, "text/plain", "Missing arguments");
        }
    });

    server.on("/fireflyEffect", HTTP_POST, []() {
        if (server.hasArg("d")) {
            delayTime = server.arg("d").toInt();
            startAnimation(5);
        } else {
            server.send(400, "text/plain", "Missing arguments");
        }
    });

    server.on("/starShopping", HTTP_POST, []() {
        if (server.hasArg("r") && server.hasArg("g") && server.hasArg("b") && server.hasArg("d")) {
            r = server.arg("r").toInt();
            g = server.arg("g").toInt();
            b = server.arg("b").toInt();
            delayTime = server.arg("d").toInt();
            startAnimation(6);
        } else {
            server.send(400, "text/plain", "Missing arguments");
        }
    });

    server.onNotFound(notFound);
    server.begin();
    Serial.println("Server started.");
}

void loop() {
    server.handleClient();

    if (animationRunning) {
        runAnimation(currentAnimation);
    }
}