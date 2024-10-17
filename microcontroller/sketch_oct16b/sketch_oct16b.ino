#include <Arduino.h>
#include <Wire.h>
#include <SparkFun_VEML6030_Ambient_Light_Sensor.h>  // include sensor lib
#include <ESPAsyncWebServer.h>
#include <WiFi.h>
 

const char* ssid = "SSID";
const char* password = "PASSWORD";
AsyncWebServer server(80);
 
int DIR1 = 15;
int PWM1 = 16;
int LED_PIN = 26;  // LED connects to GPIO26
int motor_speed = 150;
String motor_state = "up";
String led_state = "off";

bool manualMode = false; // Manual mode flag
 
SparkFun_Ambient_Light lightSensor(0x10);  // sensor created

 
void setup() {
    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(LED_PIN, OUTPUT);
    Serial.begin(115200);
 
    delay(3000);
    Serial.println(F("Starting"));
    analogWrite(PWM1, 0);
    pinMode(DIR1, OUTPUT);
    pinMode(PWM1, OUTPUT);
 
    Wire.begin();  //initialize I2C
    Serial.println("Initializing light sensor...");
    if (!lightSensor.begin()) {
        Serial.println("Light sensor not detected, check connections.");
        while (1);  // if sensor not detected，continue looping
    }
    Serial.println("Light sensor initialized successfully.");
  
  // Connect to the open Wi-Fi network
  WiFi.begin(ssid, password);
  Serial.println("Connecting to WiFi...");
  // Wait until the ESP32 is connected to the Wi-Fi
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting...");
  }

  // Once connected, print the local IP address
  Serial.println("Connected to WiFi!");
  Serial.print("ESP32 IP Address: ");
  Serial.println(WiFi.localIP());
  // Print the message that tells where the server is hosted
  Serial.print("Web server running on: http://");
  Serial.print(WiFi.localIP());
  Serial.println("/");

  // Configure web server routes
    server.on("/curtain/open", HTTP_GET, [](AsyncWebServerRequest *request){
        if (manualMode){
        openCurtain();
        request->send(200, "text/plain", "Curtain opened");
        return;
        } 
        request -> send(500,"text/plain","Cannot opened");
    });
 
    server.on("/curtain/close", HTTP_GET, [](AsyncWebServerRequest *request){
        if (manualMode) {
        closeCurtain();
        request->send(200, "text/plain", "Curtain closed");
        return;
        }

        request -> send(500,"text/plain","Cannot close curtain");
    });
 
    server.on("/light/on", HTTP_GET, [](AsyncWebServerRequest *request){
        if (manualMode){
        turnLightOn();
        request->send(200, "text/plain", "Light turned on");
        return;
        } 

        request -> send(500,"text/plain","Cannot open light");
    });
 
    server.on("/light/off", HTTP_GET, [](AsyncWebServerRequest *request){
        if (manualMode){
        turnLightOff();
        request->send(200, "text/plain", "Light turned off");
        return;

        } 

        request -> send(500,"text/plain","Cannot close light");
    });
 
    server.on("/manual/on", HTTP_GET, [](AsyncWebServerRequest *request){
        manualMode = true;
        request->send(200, "text/plain", "Manual mode enabled");
    });
 
    server.on("/manual/off", HTTP_GET, [](AsyncWebServerRequest *request){
        manualMode = false;
        request->send(200, "text/plain", "Manual mode disabled");
    });


     server.begin();
  Serial.println("Server started!");


}

void loop() {

    if (!manualMode){

       // test light intensity every 5secs
    float lux = lightSensor.readLight();  // read light intensity
    Serial.print("Current light intensity: ");
    Serial.print(lux);
    Serial.println(" lux");
 
    if (lux > 400.0) {
        if (motor_state != "up") {
            Serial.println("Lux above threshold; lifting curtain and turning LED OFF.");
            digitalWrite(LED_PIN, LOW);  // led off
            led_state = "off";
 
            digitalWrite(DIR1, HIGH); // Set direction to "up"
            Serial.println("Direction: up");
            analogWrite(PWM1, motor_speed); // Set motor to fixed speed
            delay(5000); // Let the motor run for 5 seconds
            Serial.println("Stopping motor");
            analogWrite(PWM1, 0); // Stop the motor
            motor_state = "up";
        } else {
            Serial.println("Lux above threshold; curtain already up, LED already off. No action taken.");
        }
    } else if (lux < 100.0) {
        if (motor_state != "down") {
            Serial.println("Lux below threshold; lowering curtain and turning LED ON.");
            digitalWrite(DIR1, LOW); // Set direction to "down"
            Serial.println("Direction: down");
            analogWrite(PWM1, motor_speed); // Set motor to fixed speed
            delay(5000); // Let the motor run for 5 seconds
            Serial.println("Stopping motor");
            analogWrite(PWM1, 0); // Stop the motor
            motor_state = "down";
 
            digitalWrite(LED_PIN, HIGH);  // turn on led
            led_state = "on";
        } else {
            Serial.println("Lux below threshold; curtain already down, LED already on. No action taken.");
        }
    } else {
        Serial.println("Lux within range; keeping current state.");
    }
 
    // Wait for a short time before the next cycle
    delay(5000);

    }

   
}


// Function to open the curtain
void openCurtain() {
    motor_state = "up";
    digitalWrite(DIR1, HIGH);
    analogWrite(PWM1, motor_speed);
    delay(5000); // Simulate curtain opening time
    analogWrite(PWM1, 0);
    Serial.println("Curtain opened");
}
 
// Function to close the curtain
void closeCurtain() {
    motor_state = "down";
    digitalWrite(DIR1, LOW);
    analogWrite(PWM1, motor_speed);
    delay(5000); // Simulate curtain closing time
    analogWrite(PWM1, 0);
    Serial.println("Curtain closed");
}
 
// Function to turn on the light
void turnLightOn() {
    led_state = "on";
    digitalWrite(LED_PIN, HIGH); // Turn on LED
    Serial.println("Light turned on");
}
 
// Function to turn off the light
void turnLightOff() {
    led_state = "off";
    digitalWrite(LED_PIN, LOW); // Turn off LED
    Serial.println("Light turned off");
}
 