# LED Controller

A user-friendly LED controller that allows you to control each individual LED on an LED strip, set static colors, or play animations. This controller is based on an ESP8266 or ESP32 microcontroller and connects via Wi-Fi.

## Features:

* Control each individual LED on the strip
* Set static colors for the entire strip
* Play animated lights and effects
* Flexibility in LED arrangement (customized to the number and position of LEDs)

## Prerequisites:

* **Arduino IDE** or **VSCode with PlatformIO Extension**
* **Adafruit NeoPixel Library** for controlling the LEDs
* **Wi-Fi connection** to control LEDs remotely

## Setup:

### 1. Install Arduino IDE or PlatformIO:

* Download **[Arduino IDE](https://www.arduino.cc/en/software)**, or
* Install **[PlatformIO](https://platformio.org/)** as an extension in **VSCode**.

### 2. Open the `main.cpp` file:

* Open the file in either **Arduino IDE** or **VSCode with PlatformIO**.

### 3. Install the required library:

* Download the **Adafruit NeoPixel Library** for Arduino IDE or PlatformIO:

  * **Arduino IDE**: Go to **Sketch > Include Library > Manage Libraries**, search for "Adafruit NeoPixel" and install it.
  * **PlatformIO**: Add the following line to your `platformio.ini` file:

    ```ini
    lib_deps = Adafruit NeoPixel
    ```

### 4. Restart your IDE:

* Close and reopen Arduino IDE or VSCode to ensure the library loads correctly.

### 5. Configure your Wi-Fi and LED strip settings:

* Replace the placeholders in `main.cpp` with your own details:

  ```cpp
  const char* ssid = "";       // (line 16)
  const char* password = "";   // (line 17)
  #define LED_PIN 2            // (line 20)
  #define NUM_LEDS 60          // (line 21)
  ```

  * Set `ssid` to your Wi-Fi network name and `password` to your Wi-Fi password.
  * Make sure `LED_PIN` is set to the correct pin where your LED strip is connected, and `NUM_LEDS` matches the number of LEDs in your strip.

### 6. Upload the code to your Arduino:

* Connect your microcontroller (ESP8266 or ESP32) to your computer.
* Upload the code by clicking **Upload** in Arduino IDE or PlatformIO.

---

## Usage:

### 1. Download and Setup:

* Download the executable file `main.exe` from this repository.
* Create a folder on your computer, for example: `C:/LED-Controller`.
* Copy the downloaded `main.exe` into that folder.

### 2. Connect the Arduino and LED strip:

* Connect the microcontroller and the LED strip.
* Ensure the LED strip is powered on.

### 3. Launch the application:

* Run `main.exe`.
* Your LEDs should now be controllable via Wi-Fi.

### 4. Control:

* **Individual LED Control**: You can control each LED on the strip individually, creating various colors and effects.
* **Static Colors**: Set a static color for the entire strip.
* **Animations**: Play different light effects and animations, which can be adjusted via the Wi-Fi control program.

---

## Notes:

* Make sure your microcontroller is powered adequately, especially when using a large number of LEDs.

---

## Enjoy controlling your LEDs!

 
