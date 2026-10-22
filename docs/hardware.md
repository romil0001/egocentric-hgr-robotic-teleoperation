# Hardware Setup

Companion notes for the MEng experimental platform (Anglia Ruskin University, 2023–24).

## Bill of materials

See [`hardware/bom.md`](../hardware/bom.md) for the costed parts list from the dissertation.

## Sensing stack (egocentric)

| Item | Notes |
|------|-------|
| Raspberry Pi 5 | Host for MediaPipe + UDP client |
| microSD 16–64 GB | Raspberry Pi OS via Raspberry Pi Imager |
| Camera module | Mounted on smart glasses / wearable frame; 1280×720 capture |
| Compatibility note | Picamera2 issues during development led to using a cable-extended camera compatible with OpenCV `VideoCapture` |

## Actuation stack

| Item | Notes |
|------|-------|
| ESP32 Dev Doit | Wi-Fi UDP endpoint |
| PCA9685 | 16-channel 12-bit PWM; channels 0–5 used |
| MG966R ×4 | Primary arm joints (~9.4–11 kg·cm stall) |
| MG90S ×2 | Lighter distal / gripper DOF |
| ABS 3D-printed links | FEA / stress discussion in dissertation Ch.3.3 (Autodesk Inventor) |

## Network

1. Place Raspberry Pi and ESP32 on the **same Wi-Fi LAN**.
2. Flash firmware with credentials in local `secrets.h` (never commit).
3. Read ESP32 IP from Serial Monitor after boot.
4. Set that IP in `software/gesture_client/config.yaml`.
5. UDP port **8266** must be reachable (no guest AP client isolation).

## Wiring sketch

```
Raspberry Pi 5 + Camera  --Wi-Fi/UDP-->  ESP32
                                           |
                                         I2C (SDA/SCL)
                                           |
                                        PCA9685
                                       / | | | | \
                                   Servo channels 0–5
```

Provide separate regulated power to PCA9685 **V+** for servos; share ground with the ESP32 logic rail.
