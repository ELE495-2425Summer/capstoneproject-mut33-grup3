# TOBB ETÜ ELE495 - Capstone Project

# Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Screenshots](#screenshots)
- [Acknowledgements](#acknowledgements)

## Introduction

The vehicle will send natural language voice commands received from the user to an artificial intelligence model (LLM). This will analyze the commands, translate them into basic driving commands, and execute these commands using sensors.

Furthermore, the vehicle will provide the user with vocal feedback, similar to natural Turkish speech (as non-robotic as possible), as the vehicle executes the commands.

The operating scenario can be briefly summarized as follows: The user gives a series of commands in natural Turkish (e.g., “engel çıkana kadar düz git, sonra sola dön, 2 saniye ileri git, sağa dön”). The vehicle's onboard microprocessor records the voice command and transcribes it using a voice recognition service. The transcribed command is analyzed using an artificial intelligence model (LLM) and converted into basic movement commands. The resulting commands are executed sequentially. The vehicle performs the assigned tasks through its motors and sensors. During the execution, the vehicle will provide users with vocal feedback in Turkish (e.g., "şu anda ileri gidiyorum", "sola dönüyorum").


## Features
List the key features and functionalities of the project.
- Hardware: The hardware components used (should be listed with links)
  - [Rasberry Pi 4](https://www.robocombo.com/raspberry-pi-4-8gb-yeni-versiyon)
  - [Raspberry Pi UPS HAT](https://market.samm.com/tr-usd/raspberry-pi-ups-hat)
  - [Raspberry Pi  Sd Kart](https://market.samm.com/raspberry-pi-64gb-a2-class-hafiza-karti)
  - [Micro SD Hafıza Kart Okuyucu](https://www.hepsiburada.com/veggieg-usb-2-0-sd-ve-micro-sd-hafiza-kart-okuyucu-siyah-p-HBCV000075WAZD)
  - [HC-SR04 Arduino Ultrasonic Mesafe Sensörü](https://robolinkmarket.com/hc-sr04-arduino-ultrasonic-mesafe-sensoru?srsltid=AfmBOooZNz0LNqoCOcTf4P2N2B-U-qGTtOwfh3LrpjtQ432j951cvKpiRXQ&gStoreCode=robolinkG1)
  - [L298N Motor Sürücü Kartı](https://robolinkmarket.com/l298n-motor-surucu-karti?srsltid=AfmBOoprUP9nhtKZ9o601lqJdaMOPEYprGBfUbroT7UoArpduLZ_hXtT6Pk&gStoreCode=robolinkG1)
  - [Arduino Nano](https://www.robotistan.com/arduino-nano?language=tr&h=1617316c)
  - [MPU9250 9 Eksenli Gyro ve Eğim Sensörü](https://www.robocombo.com/mpu-9250-9-eksen-jiroskop-ivmeolcer-manyetometre-sensor-modulu?srsltid=AfmBOorEJfvat3dhbArzxP1OZkIcCixFGoXX8n1p_biLCCXOeLeWURcTlkw)
  - [Mikrofon](https://www.hepsiburada.com/daytona-k9-c2-wireless-3in1-kablosuz-mikrofon-type-c-lightning-3-5mm-jak-ciftli-yaka-mikrofonu-p-HBCV00004625CL?magaza=Alcamseni)
  - [Hoparlör](https://www.hepsiburada.com/grundig-solo-bluetooth-hoparlor-siyah-p-HBCV000051RRB7)
  - [Servo Motor](https://www.robocombo.com/SG90-RC-Servo-Motor,PR-141.html?srsltid=AfmBOoriSRx2NBEiuyk6wXhx8eV2KMV2gDN1X_tiDEVRmnpVYjCCJ1HwYyU)
  - [USB 3.1 To Type-C Dönüştürücü](https://www.hepsiburada.com/baseus-usb-3-1-to-type-c-donusturucu-adaptor-mini-otg-baseus-ingenuity-series-zjjq000101-p-HBCV00001TCC3G?magaza=IVOOMI)
- Operating System and packages
  - Raspberry Pi OS
  - Python 3.x
  - Windows 10 or later
- Python Libraries
  - `resemblyzer`, `speechbrain` – Speaker recognition
  - `speech_recognition`, `pyaudio` – Voice command input
  - `socket`, `json`, `datetime` – Networking and data handling
  - `numpy`, `scipy.spatial.distance` – Data processing
  - `gtts`, `subprocess` – Text-to-speech
  - `serial` (`pyserial`) – Serial communication
  - `os`, `re`, `tempfile`, `ctypes` – System utilities
  - `socketio`, `ipaddress` – WebSocket & IP
- Applications
  - Real-Time Wi-Fi Communication via TCP
  - Feasibility-Based Command Execution
  - Sequential Command Feedback Display
  - Safe Motor Activation/Deactivation
  - Authorized User Voice Verification
- Services 

## Installation
Describe the steps required to install and set up the project. Include any prerequisites, dependencies, and commands needed to get the project running.

```bash
# Example commands
git clone https://github.com/username/project-name.git
cd project-name
```

## Usage
Provide instructions and examples on how to use the project. Include code snippets or screenshots where applicable.

## Screenshots
Include screenshots of the project in action to give a visual representation of its functionality. You can also add videos of running project to YouTube and give a reference to it here. 

## Acknowledgements
Give credit to those who have contributed to the project or provided inspiration. Include links to any resources or tools used in the project.

[Contributor 1](https://github.com/user1)
[Resource or Tool](https://www.nvidia.com)
