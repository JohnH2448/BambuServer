# BambuServer
## IoT upgrade to Bambu Labs 3D printers
## Features:
- Builds new display on local hardware with customizable GUI
- Exposes interal file upload point to public facing URL
- Livestreams printing process to clients via onboard camera
- Accepts live MQTT reports to display rich data

## Description
### This repo essentially opens three background processes on a Linux device.
- A server that exposes your printer to a public facing
  url, builds and serves a simple website, holds an MQTT
  subscription to gather printer data, and streams live
  information to other processes.
- A framebuffer builder that constructs a display with
  rich data about print status, system info, etc. With
  required hardware, it pushes this to a small HDMI screen
  so you can view the full display in real life.
- A background RTSP handler that accepts camera frames
  and streams them to website clients so the print can
  be viewed live via web. This can also be integrated
  into the HDMI screen if desired. 

## Hardware Requirements
- Linux System (Rasberry Pi 4)
- 1.05.00 Firmware (Tested)
- Mini LCD Display (Built for 1024x600)
- HDMI and USB-C Cables
- Bambu Labs Printer (Tested with A1)

## Setup
1) Generate cert file for TLS, name it "blcert.pem", replace in directory

2) Flash Rasberry Pi with Lite OS and connect via SSH

3) Run the following in a terminal
   sudo chvt 2
   sudo systemctl stop getty@tty2.service
   sudo bash -c 'clear > /dev/tty2'
   sudo bash -c 'setterm -cursor off > /dev/tty2'
   
4) Install Python3, Git, and Bambu-go2rtc on Linux Server
   
   sudo apt install -y git
   sudo apt install -y python3
   git clone https://github.com/synman/bambu-go2rtc
   
5) Launch Linux go2rtc process in new terminal

   PRINTER_ADDRESS=<INSERT_PRINTER_IP> PRINTER_ACCESS_CODE=<INSTERT_PRINTER_ACCESS_CODE> ./go2rtc_linux_arm64 -config ./go2rtc.yaml

6) Fill out .env variables
   
   IP = Printer IP Address
   ACCESS_CODE = Printer Access Code
   SERIAL = Printer Serial Number
   CONTROLLER_IP = Server IP

7) Create venv and install Python requirements (requirements.txt)

8) Go to wifi router settings and configure server and printer IPs as fixed
   
9) Launch Flask server "mqtt.py" in new terminal

echo 0 | sudo tee /sys/class/vtconsole/vtcon1/bind

