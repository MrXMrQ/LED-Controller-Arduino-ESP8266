#include <Arduino.h>
#include <ESP8266WebServer.h>
#include <ESP8266WiFi.h>

const char* ssid = ""; // Enter your SSID
const char* password = ""; // Enter your WiFi password

ESP8266WebServer server(80); // Create an instance of the web server on port 80

void handle_OnConnect() {
    Serial.println("Connected");   
}

void handle_ledon() {
    Serial.println("LED ON request received.");
}

void handle_ledoff() {
    Serial.println("LED OFF request received.");
}

void handle_NotFound() {
    Serial.println("404: Not Found");
}

void setup() {
    Serial.begin(115200);
    Serial.println("");
    Serial.println("Connecting to Wi-Fi...");

    // Connect to the Wi-Fi network
    WiFi.begin(ssid, password);

    // Wait until the connection is established
    while (WiFi.status() != WL_CONNECTED) {
        Serial.print(".");
        delay(1000);  // Wait for 1 second
    }

    Serial.println("WiFi connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());  // Print the IP address of the ESP8266
    
    server.on("/", handle_OnConnect);      // Handle the root URL
    server.on("/ledon", handle_ledon);     // Handle LED on request
    server.on("/ledoff", handle_ledoff);   // Handle LED off request
    server.onNotFound(handle_NotFound);    // Handle all other unknown routes

    server.begin();
    Serial.println("Server started.");
}

void loop() {
    server.handleClient();
}