/**
 * ESP32 multi-DOF robotic arm controller.
 *
 * Receives UDP gesture commands (A–I) from the Raspberry Pi / host client and
 * drives up to six servos via a PCA9685 PWM driver.
 *
 * Libraries (Arduino Library Manager):
 *   - AsyncUDP (ESP32 core)
 *   - Adafruit PWM Servo Driver Library
 *
 * Setup:
 *   1. Copy secrets.h.example → secrets.h and set Wi-Fi credentials.
 *   2. Flash with Arduino IDE (ESP32 Dev Module) or PlatformIO.
 */

#include <WiFi.h>
#include <AsyncUDP.h>
#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

#include "DataParser.h"
#include "secrets.h"

const int UDP_PORT = 8266;

DataParser dataParser;
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();
AsyncUDP udp;

const int SERVO_CH[6] = {0, 1, 2, 3, 4, 5};
int servoTarget[6] = {0, 0, 0, 0, 0, 0};
int servoAngle[6] = {0, 0, 0, 0, 0, 0};
bool servoMoving[6] = {false, false, false, false, false, false};

unsigned long lastCommandTime = 0;

#define SERVOMIN 150
#define SERVOMAX 600

void controlServos(const String& command);
void moveServoToTarget(int channel, int& currentAngle, int targetAngle, bool& moving);

void setup() {
  Serial.begin(115200);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  if (udp.listen(UDP_PORT)) {
    Serial.print("UDP Listening on port: ");
    Serial.println(UDP_PORT);
    udp.onPacket([](AsyncUDPPacket packet) {
      String incoming = "";
      for (size_t i = 0; i < packet.length(); i++) {
        incoming += (char)packet.data()[i];
      }
      dataParser.parseData(incoming, ',');
      String command = dataParser.getField(0);
      controlServos(command);
      lastCommandTime = millis();
    });
  }

  pwm.begin();
  pwm.setPWMFreq(60);
}

void loop() {
  // Safety: stop incremental motion if no command for >1 s
  if (millis() - lastCommandTime > 1000) {
    for (int i = 0; i < 6; i++) {
      servoMoving[i] = false;
    }
  }

  for (int i = 0; i < 6; i++) {
    moveServoToTarget(SERVO_CH[i], servoAngle[i], servoTarget[i], servoMoving[i]);
  }
  delay(15);
}

void controlServos(const String& command) {
  if (command == "A") {
    servoTarget[0] = 180;
    servoMoving[0] = true;
  } else if (command == "B") {
    servoTarget[1] = 180;
    servoMoving[1] = true;
  } else if (command == "C") {
    servoTarget[2] = 180;
    servoMoving[2] = true;
  } else if (command == "D") {
    servoTarget[3] = 180;
    servoMoving[3] = true;
  } else if (command == "E") {
    servoTarget[4] = 180;
    servoMoving[4] = true;
  } else if (command == "F") {
    servoTarget[5] = 180;
    servoMoving[5] = true;
  } else if (command == "G") {
    servoTarget[5] = 0;
    servoMoving[5] = true;
  } else if (command == "H") {
    servoTarget[0] = 45;
    servoTarget[1] = 60;
    servoTarget[2] = 100;
    servoTarget[3] = 45;
    servoTarget[4] = 90;
    for (int i = 0; i < 5; i++) {
      servoMoving[i] = true;
    }
  } else if (command == "I") {
    for (int i = 0; i < 6; i++) {
      servoMoving[i] = false;
    }
  }
}

void moveServoToTarget(int channel, int& currentAngle, int targetAngle, bool& moving) {
  if (!moving) {
    return;
  }
  if (currentAngle < targetAngle) {
    currentAngle++;
  } else if (currentAngle > targetAngle) {
    currentAngle--;
  } else {
    moving = false;
    return;
  }
  int pulseWidth = map(currentAngle, 0, 180, SERVOMIN, SERVOMAX);
  pwm.setPWM(channel, 0, pulseWidth);
}
