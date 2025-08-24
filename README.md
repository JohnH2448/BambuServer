# BambuServer
## IoT upgrade to Bambu Labs 3D printers
## Features:
- Builds new display on local hardware with customizable GUI
- Exposes interal file upload point to public facing URL
- Livestreams printing process to clients via onboard camera
- Accepts live MQTT reports to display rich data

## Hardware Requirements
- Linux System (Rasberry Pi 4)
- 1.05.00 Firmware (Tested)
- Mini LCD Display (Built for 1024x600)
- HDMI and USB-C Cables
- Bambu Labs Printer (Tested with A1)

## Setup
1) Generate cert file for TLS, name it "blcert.pem", replace in directory
   
2) Install Python3, Git, and Bambu-go2rtc on Linux Server
   
   sudo apt install -y git
   sudo apt install -y python3
   git clone https://github.com/synman/bambu-go2rtc
   
3) Launch Linux go2rtc process in new terminal

   PRINTER_ADDRESS=<INSERT_PRINTER_IP> PRINTER_ACCESS_CODE=<INSTERT_PRINTER_ACCESS_CODE> ./go2rtc_linux_arm64 -config ./go2rtc.yaml

4) Fill out .env variables
   
   IP = Printer IP Address
   ACCESS_CODE = Printer Access Code
   SERIAL = Printer Serial Number
   CONTROLLER_IP = Server IP

5) Create venv and install Python requirements (requirements.txt)

6) Go to wifi router settings and configure server and printer IPs as fixed
   
7) Launch Flask server "mqtt.py" in new terminal
