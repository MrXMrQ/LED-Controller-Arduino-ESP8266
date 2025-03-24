#include <Arduino.h>
#include <ESP8266WebServer.h>
#include <ESP8266WiFi.h>
#include <Adafruit_NeoPixel.h>

/**
 * @file LedStripControl.ino
 * @brief ESP8266-based LED strip controller with animations and web server control.
 *
 * This program connects to a Wi-Fi network and provides a web server to control an LED strip.
 * Users can turn LEDs on/off, adjust brightness, and trigger animations like running lights,
 * breathing light, and rainbow wave.
 */

// WiFi Credentials
const char* ssid = "";  // Wi-Fi SSID
const char* password = "";  // Wi-Fi Password

ESP8266WebServer server(80);  // Web server on port 80

// LED Strip Configuration
#define LED_PIN 2  // Pin connected to LED strip
#define NUM_LEDS 60  // Number of LEDs in the strip

Adafruit_NeoPixel strip(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);

// Animation Control Variables
bool animationRunning = false;
int currentAnimation = -1;
uint32_t lastUpdate = 0;

// LED Parameters
uint8_t r = 255, g = 0, b = 0, r1 = 255, g1 = 0, b1 = 0;
int brightness = 50;
unsigned long delayTime = 10;

/**
 * @brief Stops any ongoing animation and clears the LED strip.
 */
void stopAnimation() {
    Serial.println("Stopping animation.");
    animationRunning = false;
    currentAnimation = -1;
    strip.show();
    server.send(200, "text/plain", "Animation stopped!");
}

/**
 * @brief Sets all LEDs to a specified color.
 * @param color The color to set all LEDs to.
 */
void setAllLeds(uint32_t color) {
    for (int i = 0; i < NUM_LEDS; i++) {
        strip.setPixelColor(i, color);
    }
    strip.show();
}

/**
 * @brief Turns the LEDs on with the specified color and brightness.
 */
void ledOn() {
    stopAnimation();
    Serial.println("Turning LEDs on.");
    strip.setBrightness(brightness);
    setAllLeds(strip.Color(r, g, b));
    server.send(200, "text/plain", "LEDs on");
}

/**
 * @brief Turns the LEDs off.
 */
void ledOff() {
    Serial.println("Turning LEDs off.");
    animationRunning = false;
    currentAnimation = -1;
    strip.clear();
    strip.show();
    server.send(200, "text/plain", "LEDs off");
}

void responseESP() {
    server.send(200, "text/plain", "webserver online");    
}

/**
 * @brief Handles unknown web requests.
 */
void notFound() {
    Serial.println("404 Not Found");
    server.send(404, "text/plain", "404 - Request not found");
}

/**
 * @brief Running Lights animation.
 */
void runningLights() {
    static int position = 0;
    if (millis() - lastUpdate > delayTime) {
        lastUpdate = millis();
        strip.clear();
        strip.setPixelColor(position, strip.Color(r, g, b));
        strip.show();
        position = (position + 1) % NUM_LEDS;
    }
}

/**
 * @brief Breathing Light animation.
 */
void breathingLight() {
    static int step = 0;
    static bool increasing = true;
    if (millis() - lastUpdate > delayTime) {
        lastUpdate = millis();
        uint8_t level = (brightness * step) / 255;
        setAllLeds(strip.Color(r * level / 255, g * level / 255, b * level / 255));
        step += increasing ? 5 : -5;
        if (step >= 255 || step <= 0) increasing = !increasing;
    }
}

/**
 * @brief Rainbow Wave animation.
 */
void rainbowWave() {
    static uint16_t hue = 0;
    if (millis() - lastUpdate > delayTime) {
        lastUpdate = millis();
        for (int i = 0; i < NUM_LEDS; i++) {
            strip.setPixelColor(i, strip.ColorHSV(hue + (i * 65536 / NUM_LEDS), 255, brightness));
        }
        strip.show();
        hue += 256;
    }
}

/**
 * @brief Gradient Wave Animation. Smoothly transitions from color A to color B and back.      
 */
void gradiant() {
    static uint8_t step = 0;
    static bool forward = true;

    if (millis() - lastUpdate > delayTime) {
        lastUpdate = millis();

        uint8_t blend = step;
        for (int i = 0; i < NUM_LEDS; i++) {
            uint8_t rMix = (r * (255 - blend) + r1 * blend) / 255;
            uint8_t gMix = (g * (255 - blend) + g1 * blend) / 255;
            uint8_t bMix = (b * (255 - blend) + b1 * blend) / 255;
            strip.setPixelColor(i, strip.Color(rMix, gMix, bMix));
        }
        strip.show();

        step += forward ? 5 : -5;

        if (step >= 255 || step <= 0) {
            forward = !forward;
        }
    }
}

/**
 * @brief Firefly Animation. Simulates the flickering effect of a fireplace.       
 */
void fireplace() {
    if (millis() - lastUpdate > delayTime) {
        lastUpdate = millis();
        for (int i = 0; i < NUM_LEDS; i++) {
            int flicker = random(120, 255);
            strip.setPixelColor(i, strip.Color(flicker, flicker / 3, 0)); // Fire-like color
        }
        strip.show();
    }
}

/**
 * @brief Rain Animation. Random streaks of light move down like falling rain.   
 */
void rain() {
    static int drops[NUM_LEDS] = {0};
    if (millis() - lastUpdate > delayTime) {
        lastUpdate = millis();
        strip.clear();
        for (int i = 0; i < NUM_LEDS; i++) {
            if (random(100) < 5) { // 5% chance to start a new drop
                drops[i] = random(3, 8); // Drop length
            }
            if (drops[i] > 0) {
                strip.setPixelColor(i, strip.Color(r, g, b)); // Blue raindrop
                drops[i]--;
            }
        }
        strip.show();
    }
}

/**
 * @brief Executes the selected animation.
 */
void runAnimation() {
    switch (currentAnimation) {
        case 0: runningLights(); break;
        case 1: breathingLight(); break;
        case 2: rainbowWave(); break;
        case 3: gradiant(); break;
        case 4: fireplace(); break;
        case 5: rain(); break;
    }
}

/**
 * @brief Extracts parameters from HTTP request.
 * @return true if all required parameters are present, false otherwise.
 */
bool extractArguments() {
    if (server.hasArg("r") && server.hasArg("g") && server.hasArg("b") && server.hasArg("br") && server.hasArg("d")) {
        r = server.arg("r").toInt();
        g = server.arg("g").toInt();
        b = server.arg("b").toInt();
        brightness = server.arg("br").toInt();
        delayTime = server.arg("d").toInt();
        return true;
    }
    server.send(400, "text/plain", "Missing arguments");
    return false;
}

/**
 * @brief Starts an animation.
 * @param animationIndex The index of the animation to start.
 */
void startAnimation(int animationIndex) {
    Serial.printf("Starting animation %d\n", animationIndex);
    currentAnimation = animationIndex;
    animationRunning = true;
    server.send(200, "text/plain", "Animation started!");
}

void setup() {
    Serial.begin(115200);
    Serial.println("Connecting to Wi-Fi...");
    WiFi.begin(ssid, password);
    strip.begin();

    while (WiFi.status() != WL_CONNECTED) {
        Serial.print(".");
        delay(500);
    }
    strip.fill(strip.Color(255,255,255), 0, NUM_LEDS);
    strip.setBrightness(10);
    strip.show();

    Serial.println("\nWiFi connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());

    server.on("/ledOn", HTTP_POST, []() { if (extractArguments()) ledOn(); });
    server.on("/ledOff", ledOff);
    server.on("/esp8266", responseESP);
    server.on("/stop", stopAnimation);
    server.onNotFound(notFound);

    server.on("/runningLights", HTTP_POST, []() { if (extractArguments()) startAnimation(0); });
    server.on("/breathingLight", HTTP_POST, []() { if (extractArguments()) startAnimation(1); });
    server.on("/rainbowWave", HTTP_POST, []() { if (extractArguments()) startAnimation(2); });
    server.on("/gradiant", HTTP_POST, []() { 
        if (extractArguments() && server.hasArg("r1") && server.hasArg("g1") && server.hasArg("b1")) {
            r1 = server.arg("r1").toInt(); 
            g1 = server.arg("g1").toInt(); 
            b1 = server.arg("b1").toInt(); 
            startAnimation(3); 
        } else {
            server.send(400, "text/plain", "missing args");    
        }
    });
    server.on("/firefly", HTTP_POST, []() { if (extractArguments()) startAnimation(4); });
    server.on("/rain", HTTP_POST, []() { if (extractArguments()) startAnimation(5); });

    server.begin();
    Serial.println("Server started.");
}

void loop() {
    server.handleClient();

    if (animationRunning) {
        runAnimation();
    }
}