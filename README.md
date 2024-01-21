# hand_follower_gimbal
https://github.com/axcerruto/hand_follower_gimbal/assets/91328615/c5599338-75d4-47c9-b1ef-ecbfa419c9b0

## Hardware 
1. HiTec HS311 servo motors (2x)
2. Logitech C615 webcam (2x)
3. 3D printed gimbal parts
4. Arduino board (DUE board used for testing)
5. USB to TTL FTDI cable TTL-232RG-VSW5V-WE
https://ftdichip.com/product-category/products/cables/usb-ttl-serial-cable-series/

## USB to TTL Cable Signals and Connections
Color | Signal | Arduino Pin
--- | --- | ---
Black | GND | GND
Brown | CTS (Clear to send) | 7
Red | VCC (Power supply output) | 5V
Orange | Tx (Transmit) | 0
Yellow | Rx (Receive) | 1
Green | RTS (Request to send) | 8

## Install requirements:
```
python3 -m pip install numpy
python3 -m pip install opencv-python
python3 -m pip install mediapipe
```

## Motor Connections
Each servo motor has three wires: Power, GND, Signal.
First servo controls pitch angle (pin 2).
Second servo controls yaw angle (pin 13).

## Triangulation
For the math behind triangulation used in this code see: https://medium.com/@acerruto/simple-depth-sensing-with-a-dyi-stereo-camera-d4f42627f7e7
