#include <Arduino.h>
#include <ESP8266WebServer.h>
#include <ESP8266WiFi.h>
#include <Adafruit_NeoPixel.h>
#include <EEPROM.h>

/**
 * @file LedStripControl.ino
 * @brief ESP8266-based LED strip controller with animations, web server control, and state saving.
 *
 * This program connects to a Wi-Fi network and provides a web server to control an LED strip.
 * Users can turn LEDs on/off, adjust brightness, and trigger animations. The program saves the
 * last state to EEPROM and restores it on power-up.
 */

// WiFi Credentials
const char* ssid = "";  // Wi-Fi SSID
const char* password = "";  // Wi-Fi Password

// LED Strip Configuration
#define LED_PIN 2       // Pin connected to LED strip
#define NUM_LEDS 60     // Number of LEDs in the strip

// EEPROM Configuration
#define EEPROM_SIZE 64  // Space needed to store our configuration
#define EEPROM_MAGIC 0xAB // Magic number to verify valid EEPROM data

// Animation Types
enum AnimationType {
  NONE = -1,
  RAINBOW = 0,
  PULSE = 1,
  CHASING = 2,
  STROBE = 3,
  RAINDROP = 4,
  FIREPLACE = 5
};

// Structure to store LED state in EEPROM
struct LEDState {
  uint8_t magic;         // Magic number to verify valid data
  bool isOn;             // Whether LEDs are on or off
  uint8_t r;             // Red component
  uint8_t g;             // Green component
  uint8_t b;             // Blue component
  uint8_t brightness;    // Brightness level
  int animationType;     // Current animation
  unsigned long delayTime; // Animation delay
};

// Web server on port 80
ESP8266WebServer server(80);

// Initialize LED strip
Adafruit_NeoPixel strip(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);

// Animation Control Variables
bool animationRunning = false;
AnimationType currentAnimation = NONE;
uint32_t lastUpdate = 0;

// LED Parameters
uint8_t r = 255, g = 0, b = 0;
int brightness = 50;
unsigned long delayTime = 10;
bool isOn = false;

// State for default yellow lights on first 5 LEDs
bool isDefaultState = true;

// Animation-specific variables
struct {
  // Rainbow animation
  uint16_t hue = 0;
  
  // Pulse animation
  int step = 0;
  bool increasing = true;
  
  // Chasing animation
  int position = 0;
  
  // Strobe animation
  bool strobeState = false;
  unsigned long lastStrobeTime = 0;
  unsigned long strobeOnTime = 50;
  unsigned long strobeOffTime = 150;
  
  // Raindrop animation
  int drops[NUM_LEDS] = {0};
} animationVars;

// Function Prototypes
void setupWiFi();
void setupServer();
void setupLEDs();
bool extractArguments();
void stopAnimation();
void setAllLeds(uint32_t color);
void runAnimation();
void saveState();
bool loadState();
void setDefaultState();

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
 * @brief Stops any ongoing animation and clears the LED strip.
 */
void stopAnimation() {
  Serial.println("Stopping animation.");
  animationRunning = false;
  currentAnimation = NONE;
  // Don't clear strip - let the calling function decide what to do with the LEDs
}

/**
 * @brief Turns the LEDs on with the specified color and brightness.
 */
void ledOn() {
  stopAnimation();
  Serial.println("Turning LEDs on.");
  isOn = true;
  isDefaultState = false;
  strip.setBrightness(brightness);
  setAllLeds(strip.Color(r, g, b));
  saveState();
  server.send(204); // No content response
}

/**
 * @brief Turns the LEDs off.
 */
void ledOff() {
  Serial.println("Turning LEDs off.");
  stopAnimation();
  isOn = false;
  isDefaultState = false;
  strip.clear();
  strip.show();
  saveState();
  server.send(204); // No content response
}

/**
 * @brief Sets the default state (first 5 LEDs yellow)
 */
void setDefaultState() {
  Serial.println("Setting default state (first 5 LEDs yellow)");
  strip.clear();
  strip.setBrightness(25);
  
  // Set first 5 LEDs to yellow
  for (int i = 0; i < 5; i++) {
    strip.setPixelColor(i, strip.Color(255, 255, 0)); // Yellow color (R+G)
  }
  
  strip.show();
  isDefaultState = true;
  isOn = true;
  currentAnimation = NONE;
  animationRunning = false;
}

/**
 * @brief Returns the MAC address of the device.
 */
void getMac() {
  server.send(200, "text/plain", WiFi.macAddress());
}

/**
 * @brief Returns the NUM_LEDS of the strip.
 */
void getLEDs() {
  server.send(200, "text/plain", String(NUM_LEDS));
}

/**
 * @brief Handles unknown web requests.
 */
void notFound() {
  server.send(404, "text/plain", "404 - Request not found");
}

/**
 * @brief Rainbow Wave animation.
 */
void rainbow() {
  if (millis() - lastUpdate > delayTime) {
    lastUpdate = millis();
    for (int i = 0; i < NUM_LEDS; i++) {
      strip.setPixelColor(i, strip.ColorHSV(animationVars.hue + (i * 65536 / NUM_LEDS), 255, brightness));
    }
    strip.show();
    animationVars.hue += 256;
  }
}

/**
 * @brief Breathing Light animation.
 */
void pulse() {
  if (millis() - lastUpdate > delayTime) {
    lastUpdate = millis();
    uint8_t level = (brightness * animationVars.step) / 255;
    setAllLeds(strip.Color(r * level / 255, g * level / 255, b * level / 255));
    
    animationVars.step += animationVars.increasing ? 5 : -5;
    if (animationVars.step >= 255 || animationVars.step <= 0) {
      animationVars.increasing = !animationVars.increasing;
    }
  }
}

/**
 * @brief Running Lights animation.
 */
void chasing() {
  if (millis() - lastUpdate > delayTime) {
    lastUpdate = millis();
    strip.clear();
    strip.setPixelColor(animationVars.position, strip.Color(r, g, b));
    strip.show();
    animationVars.position = (animationVars.position + 1) % NUM_LEDS;
  }
}

/**
 * @brief Strobe animation that alternates between on and off states.
 */
void strobe() {
  unsigned long currentTime = millis();
  
  if (animationVars.strobeState) {
    // If strobe is ON and time to turn OFF
    if (currentTime - animationVars.lastStrobeTime > animationVars.strobeOnTime) {
      strip.clear();
      strip.show();
      animationVars.strobeState = false;
      animationVars.lastStrobeTime = currentTime;
    }
  } else {
    // If strobe is OFF and time to turn ON
    if (currentTime - animationVars.lastStrobeTime > animationVars.strobeOffTime) {
      setAllLeds(strip.Color(r, g, b));
      animationVars.strobeState = true;
      animationVars.lastStrobeTime = currentTime;
    }
  }
}

/**
 * @brief Rain Animation. Random streaks of light move down like falling rain.   
 */
void raindrop() {
  if (millis() - lastUpdate > delayTime) {
    lastUpdate = millis();
    strip.clear();
    for (int i = 0; i < NUM_LEDS; i++) {
      if (random(100) < 5) { // 5% chance to start a new drop
        animationVars.drops[i] = random(3, 8); // Drop length
      }
      if (animationVars.drops[i] > 0) {
        strip.setPixelColor(i, strip.Color(r, g, b));
        animationVars.drops[i]--;
      }
    }
    strip.show();
  }
}

/**
 * @brief Firefly Animation. Simulates the flickering effect of a fireplace.       
 */
void fireplace() {
  if (millis() - lastUpdate > delayTime) {
    lastUpdate = millis();

    int numColors = 4;
    int step = 255 / numColors;

    uint32_t similarColors[numColors];
    int index = 0;

    for (int i = -numColors / 2; i <= numColors / 2; i++) {
      int newR = constrain(r + i * step, 0, 255);
      int newG = constrain(g + i * step, 0, 255);
      int newB = constrain(b + i * step, 0, 255);
      similarColors[index++] = strip.Color(newR, newG, newB);
    }

    for (int i = 0; i < NUM_LEDS; i++) {
      int randomIndex = random(0, numColors);
      strip.setPixelColor(i, similarColors[randomIndex]); // Fire-like color
    }
    strip.show();
  }
}

/**
 * @brief Executes the selected animation.
 */
void runAnimation() {
  switch (currentAnimation) {
    case RAINBOW:
      rainbow();
      break;
    case PULSE:
      pulse();
      break;
    case CHASING:
      chasing();
      break;
    case STROBE:
      strobe();
      break;
    case RAINDROP:
      raindrop();
      break;
    case FIREPLACE:
      fireplace();
      break;
    case NONE:
    default:
      // No animation running
      break;
  }
}

/**
 * @brief Extracts parameters from HTTP request.
 * @return true if all required parameters are present, false otherwise.
 */
bool extractArguments() {
  if (server.hasArg("r") && server.hasArg("g") && server.hasArg("b") && 
      server.hasArg("br") && server.hasArg("d")) {
    r = server.arg("r").toInt();
    g = server.arg("g").toInt();
    b = server.arg("b").toInt();
    brightness = server.arg("br").toInt();
    delayTime = server.arg("d").toInt();
    
    // Validate parameters
    r = constrain(r, 0, 255);
    g = constrain(g, 0, 255);
    b = constrain(b, 0, 255);
    brightness = constrain(brightness, 0, 255);
    delayTime = constrain(delayTime, 1, 1000);
    
    return true;
  }
  server.send(400, "text/plain", "Missing arguments");
  return false;
}

/**
 * @brief Starts an animation.
 * @param animationIndex The animation type to start.
 */
void startAnimation(AnimationType animationType) {
  Serial.printf("Starting animation %d\n", animationType);
  
  // Reset animation-specific variables
  switch (animationType) {
    case STROBE:
      animationVars.strobeState = false;
      animationVars.lastStrobeTime = millis();
      break;
    case PULSE:
      animationVars.step = 0;
      animationVars.increasing = true;
      break;
    default:
      break;
  }
  
  isDefaultState = false;
  isOn = true;
  currentAnimation = animationType;
  animationRunning = true;
  strip.setBrightness(brightness);
  
  // Save state to EEPROM
  saveState();
  
  server.send(200, "text/plain", "Animation started!");
}

/**
 * @brief Saves the current LED state to EEPROM
 */
void saveState() {
  LEDState state;
  state.magic = EEPROM_MAGIC;
  state.isOn = isOn;
  state.r = r;
  state.g = g;
  state.b = b;
  state.brightness = brightness;
  state.animationType = (int)currentAnimation;
  state.delayTime = delayTime;
  
  // Write the structure to EEPROM
  EEPROM.put(0, state);
  EEPROM.commit();
  
  Serial.println("State saved to EEPROM");
}

/**
 * @brief Loads the LED state from EEPROM
 * @return true if valid state was loaded, false otherwise
 */
bool loadState() {
  LEDState state;
  EEPROM.get(0, state);
  
  // Check if the saved data is valid
  if (state.magic != EEPROM_MAGIC) {
    Serial.println("No valid state found in EEPROM");
    return false;
  }
  
  // Restore the state
  isOn = state.isOn;
  r = state.r;
  g = state.g;
  b = state.b;
  brightness = state.brightness;
  currentAnimation = (AnimationType)state.animationType;
  delayTime = state.delayTime;
  
  Serial.println("State loaded from EEPROM");
  Serial.printf("LEDs: %s, R: %d, G: %d, B: %d, Brightness: %d, Animation: %d\n", 
                isOn ? "ON" : "OFF", r, g, b, brightness, currentAnimation);
  
  // Apply the loaded state
  if (isOn) {
    strip.setBrightness(brightness);
    if (currentAnimation != NONE) {
      animationRunning = true;
    } else {
      setAllLeds(strip.Color(r, g, b));
    }
  } else {
    strip.clear();
    strip.show();
  }
  
  return true;
}

/**
 * @brief Set up WiFi connection
 */
void setupWiFi() {
  Serial.println("Connecting to Wi-Fi...");
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
  
  Serial.println("\nWiFi connected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

/**
 * @brief Set up LED strip
 */
void setupLEDs() {
  strip.begin();
  strip.clear();
  strip.show();
}

/**
 * @brief Set up web server routes
 */
void setupServer() {
  // Basic LED control
  server.on("/ledOn", HTTP_POST, []() { 
    if (extractArguments()) ledOn(); 
  });
  server.on("/ledOff", HTTP_POST, ledOff);
  server.on("/mac", HTTP_GET, getMac);
  server.on("/num", HTTP_GET, getLEDs);
  server.on("/default", HTTP_POST, []() {
    setDefaultState();
    saveState();
    server.send(200, "text/plain", "Reset to default state");
  });

  // Animation endpoints
  server.on("/rainbow", HTTP_POST, []() { 
    if (extractArguments()) startAnimation(RAINBOW); 
  });
  server.on("/pulse", HTTP_POST, []() { 
    if (extractArguments()) startAnimation(PULSE); 
  });
  server.on("/chasing", HTTP_POST, []() { 
    if (extractArguments()) startAnimation(CHASING); 
  });
  server.on("/strobe", HTTP_POST, []() { 
    if (extractArguments()) startAnimation(STROBE); 
  });
  server.on("/raindrop", HTTP_POST, []() { 
    if (extractArguments()) startAnimation(RAINDROP); 
  });
  server.on("/fireplace", HTTP_POST, []() { 
    if (extractArguments()) startAnimation(FIREPLACE); 
  });
  
  server.onNotFound(notFound);
  server.begin();
  Serial.println("Server started.");
}

void setup() {
  Serial.begin(115200);
  
  // Initialize EEPROM
  EEPROM.begin(EEPROM_SIZE);
  
  setupLEDs();
  setupWiFi();
  setupServer();
  
  // Try to load saved state, or use default if no valid state is found
  if (!loadState()) {
    setDefaultState();
  } else {
    isDefaultState = false;
  }
}

void loop() {
  server.handleClient();

  if (animationRunning) {
    runAnimation();
  }
}