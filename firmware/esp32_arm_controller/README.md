# ESP32 Arm Controller Firmware

UDP-driven servo controller for a 6-channel PCA9685 robotic arm.

## Dependencies

Install via Arduino Library Manager:

| Library | Purpose |
|---------|---------|
| **Adafruit PWM Servo Driver** | PCA9685 I²C PWM |
| **AsyncUDP** | Non-blocking UDP (ESP32 Arduino core) |

Board: **ESP32 Dev Module** (DOIT DevKit style).

## Secrets

```bash
cp secrets.h.example secrets.h
# edit WIFI_SSID / WIFI_PASSWORD
```

`secrets.h` is gitignored. Never commit credentials.

## Protocol

- **Port:** `8266`
- **Payload:** `"<CMD>,100,0,0,0"` (comma-separated; field 0 is the command)
- **Commands:** `A`–`I` (see repository `docs/architecture.md`)

## Wiring (summary)

| ESP32 | PCA9685 |
|-------|---------|
| 3V3 / 5V (per board) | VCC |
| GND | GND |
| SDA (GPIO 21 typical) | SDA |
| SCL (GPIO 22 typical) | SCL |

Servos on PCA9685 channels `0`–`5`. Use a dedicated servo supply on PCA9685 `V+`.

## Bench test without camera

From the repo root (host on the same Wi-Fi):

```bash
python scripts/simulate_udp_sender.py --host <ESP32_IP> --command B
```
