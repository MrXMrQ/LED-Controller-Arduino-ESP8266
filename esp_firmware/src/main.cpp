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

// Structure for individual LED data
struct LEDPixelData {
  bool isSet;     // LED has individual setting
  uint8_t r;      // Red component
  uint8_t g;      // Green component
  uint8_t b;      // Blue component
};


LEDPixelData pixelData[NUM_LEDS];

// EEPROM Configuration
#define EEPROM_SIZE (64 + (sizeof(LEDPixelData) * NUM_LEDS))  // Space needed to store our configuration
#define EEPROM_MAGIC 0xAB // Magic number to verify valid EEPROM data
#define LED_DATA_OFFSET 64 // Offset for storing individual LED data in EEPROM

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

struct LEDState {
  uint8_t magic;         
  bool isOn;             // LEDs are on or off
  uint8_t r;             // Red component
  uint8_t g;             // Green component
  uint8_t b;             // Blue component
  unsigned long delayTime; // Animation delay
  int animationType;     // Current animation
  bool hasIndividualLEDs; // Flag indicating if individual LEDs are set
};

ESP8266WebServer server(80);

Adafruit_NeoPixel strip(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);

bool animationRunning = false;
AnimationType currentAnimation = NONE;
uint32_t lastUpdate = 0;

uint8_t r = 255, g = 0, b = 0;
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
void saveIndividualLEDs();
void loadIndividualLEDs();

/**
 * @brief Saves the individual LED data to EEPROM
 */
void saveIndividualLEDs() {
  int address = LED_DATA_OFFSET;
  
  for (int i = 0; i < NUM_LEDS; i++) {
    EEPROM.put(address, pixelData[i]);
    address += sizeof(LEDPixelData);
  }
  
  EEPROM.commit();
  Serial.println("Individual LED data saved");
}

/**
 * @brief Loads the individual LED data from EEPROM
 */
void loadIndividualLEDs() {
  int address = LED_DATA_OFFSET;
  
  for (int i = 0; i < NUM_LEDS; i++) {
    EEPROM.get(address, pixelData[i]);
    address += sizeof(LEDPixelData);
  }
  
  Serial.println("Individual LED data loaded");
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
 * @brief Stops any ongoing animation and clears the LED strip.
 */
void stopAnimation() {
  Serial.println("Stopping animation.");
  animationRunning = false;
  currentAnimation = NONE;
}

/**
 * @brief Turns the LEDs on with the specified color and brightness.
 */
void ledOn() {
  stopAnimation();
  Serial.println("Turning LEDs on.");
  isOn = true;
  isDefaultState = false;
  
  for (int i = 0; i < NUM_LEDS; i++) {
    pixelData[i].isSet = false;
  }
  
  setAllLeds(strip.Color(r, g, b));
  saveState();
  server.send(204);
}

/**
 * @brief Processes the single LED request with 4-tuple format
 */
void singleLED() {
  if (server.hasArg("singleLED")) {
    String tupleStr = server.arg("singleLED");
    Serial.println("singleLED: " + tupleStr);
    
    tupleStr = tupleStr.substring(1, tupleStr.length() - 1);
    
    int startPos = 0;
    
    for (int i = 0; i < NUM_LEDS; i++) {
      pixelData[i].isSet = false;
    }
    
    strip.clear();
    
    while (true) {
      int openParenPos = tupleStr.indexOf('(', startPos);
      if (openParenPos == -1) break;
      
      int closeParenPos = tupleStr.indexOf(')', openParenPos);
      if (closeParenPos == -1) break;
      
      String innerTuple = tupleStr.substring(openParenPos + 1, closeParenPos);
      
      int ledIndex = 0;
      int r_val = 0;
      int g_val = 0;
      int b_val = 0;
      
      int commaPos = innerTuple.indexOf(',');
      if (commaPos != -1) {
        ledIndex = innerTuple.substring(0, commaPos).toInt();
        
        int lastPos = commaPos + 1;
        commaPos = innerTuple.indexOf(',', lastPos);
        if (commaPos != -1) {
          r_val = innerTuple.substring(lastPos, commaPos).toInt();
          
          lastPos = commaPos + 1;
          commaPos = innerTuple.indexOf(',', lastPos);
          if (commaPos != -1) {
            g_val = innerTuple.substring(lastPos, commaPos).toInt();
            b_val = innerTuple.substring(commaPos + 1).toInt();
          }
        }
      }
      
      ledIndex = constrain(ledIndex, 0, NUM_LEDS - 1);
      r_val = constrain(r_val, 0, 255);
      g_val = constrain(g_val, 0, 255);
      b_val = constrain(b_val, 0, 255);
      
      Serial.printf("Setting LED %d to RGB(%d, %d, %d)\n", 
                    ledIndex, r_val, g_val, b_val);
      
      pixelData[ledIndex].isSet = true;
      pixelData[ledIndex].r = r_val;
      pixelData[ledIndex].g = g_val;
      pixelData[ledIndex].b = b_val;
      
      strip.setPixelColor(ledIndex, strip.Color(r_val, g_val, b_val));
      
      startPos = closeParenPos + 1;
      
      if (tupleStr.indexOf('(', startPos) == -1) break;
    }
    
    isDefaultState = false;
    isOn = true;
    currentAnimation = NONE;
    animationRunning = false;
    strip.show();
    
    saveState();
    
    server.send(200, "text/plain", "single LEDs updated and saved");
  } else {
    server.send(400, "text/plain", "Missing parameter: singleLED");
  }
}

/**
 * @brief Turns the LEDs off.
 */
void ledOff() {
  Serial.println("Turning LEDs off.");
  stopAnimation();
  isOn = false;
  isDefaultState = false;
  
  for (int i = 0; i < NUM_LEDS; i++) {
    pixelData[i].isSet = false;
  }
  
  strip.clear();
  strip.show();
  saveState();
  server.send(204);
}

/**
 * @brief Sets the default state (first 5 LEDs yellow)
 */
void setDefaultState() {
  Serial.println("Setting default state (first 5 LEDs yellow)");
  strip.clear();
  
  for (int i = 0; i < NUM_LEDS; i++) {
    pixelData[i].isSet = false;
  }
  
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
 * @brief Rainbow animation.
 */
void rainbow() {
  if (millis() - lastUpdate > delayTime) {
    lastUpdate = millis();
    for (int i = 0; i < NUM_LEDS; i++) {
      strip.setPixelColor(i, strip.ColorHSV(animationVars.hue + (i * 65536 / NUM_LEDS), 255, 0.2126 * r + 0.7152 * g + 0.0722 * b));
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
    uint8_t level = animationVars.step;
    setAllLeds(strip.Color(r * level / 255, g * level / 255, b * level / 255));
    
    animationVars.step += animationVars.increasing ? 5 : -5;
    if (animationVars.step >= 255 || animationVars.step <= 0) {
      animationVars.increasing = !animationVars.increasing;
    }
  }
}

/**
 * @brief Chasing Lights animation.
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
    if (currentTime - animationVars.lastStrobeTime > animationVars.strobeOnTime) {
      strip.clear();
      strip.show();
      animationVars.strobeState = false;
      animationVars.lastStrobeTime = currentTime;
    }
  } else {
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
      if (random(100) < 5) {
        animationVars.drops[i] = random(3, 8);
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
 * @brief Firefly Animation. Simulates the flickering effect of a fireplace for one base color.       
 */
void fireplace() {
  if (millis() - lastUpdate > delayTime) {
    lastUpdate = millis();
    
    int numColors = 5;
    uint32_t similarColors[numColors];
    
    similarColors[0] = strip.Color(r, g, b);
    
    for (int i = 1; i < numColors; i++) {
      float brightness = 0.3 + (0.7 * i / (numColors - 1));
      
      int newR = constrain((int)(r * brightness), 0, 255);
      int newG = constrain((int)(g * brightness), 0, 255);
      int newB = constrain((int)(b * brightness), 0, 255);
      
      similarColors[i] = strip.Color(newR, newG, newB);
    }
    
    for (int i = 0; i < NUM_LEDS; i++) {
      int ledPosition = map(i, 0, NUM_LEDS - 1, 10, 0);
      int randomValue = random(0, 10);
      
      int colorIndex;
      if (randomValue < ledPosition) {
        colorIndex = random(numColors / 2, numColors);
      } else {
        colorIndex = random(0, numColors / 2);
      }
      
      strip.setPixelColor(i, similarColors[colorIndex]);
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
  if (server.hasArg("r") && server.hasArg("g") && server.hasArg("b")) {
    r = server.arg("r").toInt();
    g = server.arg("g").toInt();
    b = server.arg("b").toInt();
    
    // Validate parameters
    r = constrain(r, 0, 255);
    g = constrain(g, 0, 255);
    b = constrain(b, 0, 255);
    
    // Optional delay parameter for animations
    if (server.hasArg("delay")) {
      delayTime = server.arg("delay").toInt();
      delayTime = constrain(delayTime, 1, 1000);
    }
    
    return true;
  }
  server.send(400, "text/plain", "Missing arguments: r, g, b required");
  return false;
}

/**
 * @brief Starts an animation.
 * @param animationType The animation type to start.
 */
void startAnimation(AnimationType animationType) {
  Serial.printf("Starting animation %d\n", animationType);
  
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
  
  for (int i = 0; i < NUM_LEDS; i++) {
    pixelData[i].isSet = false;
  }
  
  isDefaultState = false;
  isOn = true;
  currentAnimation = animationType;
  animationRunning = true;
  
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
  state.delayTime = delayTime;
  state.animationType = (int)currentAnimation;
  state.hasIndividualLEDs = !isDefaultState && currentAnimation == NONE && isOn;
  
  EEPROM.put(0, state);
  
  if (state.hasIndividualLEDs) {
    saveIndividualLEDs();
  }
  
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
  
  if (state.magic != EEPROM_MAGIC) {
    Serial.println("No valid state found in EEPROM");
    return false;
  }
  
  isOn = state.isOn;
  r = state.r;
  g = state.g;
  b = state.b;
  delayTime = state.delayTime;
  currentAnimation = (AnimationType)state.animationType;
  
  Serial.println("State loaded from EEPROM");
  Serial.printf("LEDs: %s, R: %d, G: %d, B: %d, Animation: %d\n", 
                isOn ? "ON" : "OFF", r, g, b, currentAnimation);
  
  if (isOn) {
    if (state.hasIndividualLEDs) {
      loadIndividualLEDs();
      
      strip.clear();
      for (int i = 0; i < NUM_LEDS; i++) {
        if (pixelData[i].isSet) {
          strip.setPixelColor(i, strip.Color(pixelData[i].r, pixelData[i].g, pixelData[i].b));
        }
      }
      strip.show();
    } else if (currentAnimation != NONE) {
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
  server.on("/ledOn", HTTP_POST, []() { 
    if (extractArguments()) ledOn(); 
  });
  server.on("/singleLED", HTTP_POST, singleLED);
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
  EEPROM.begin(EEPROM_SIZE);
  
  setupLEDs();
  setupWiFi();
  setupServer();
  
  for (int i = 0; i < NUM_LEDS; i++) {
    pixelData[i].isSet = false;
    pixelData[i].r = 0;
    pixelData[i].g = 0;
    pixelData[i].b = 0;
  }
  
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