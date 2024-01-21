#!/usr/bin/env python3
# Created by Antonio X Cerruto 24 Feb 2022
import glob
import serial
from sys import platform
from time import sleep

BAUDRATE=250000

def port_setup():
	ser = None
	try:
		# list arduino ports: /dev/tty.usbmodem*
		if platform == 'darwin':	# MACOS
			port = glob.glob('/dev/tty.usbserial*')[0]
		else:
			port = '/dev/ttyUSB0'

		# open serial port
		ser = serial.Serial(port,
							BAUDRATE,
							rtscts=False,
							timeout=0,
							write_timeout=0)
		print(ser.name) 	# check which port was really used
		ser.reset_input_buffer()
		ser.reset_output_buffer()
	except:
		print("ERROR: no port found")
	return ser

def read_state():
	if platform == 'darwin':	# MACOS
		port = glob.glob('/dev/tty.usbserial*')[0]
	else:
		port = '/dev/ttyUSB0'
	with serial.Serial(port, BAUDRATE, rtscts=True) as ser:
		line = ser.readline()
		print(line)
	return

if __name__ == "__main__":
    # execute only if run as a script
    ser = port_setup()
    for i in range(50):
    	ser.write(('P'+str(i).zfill(3)).encode('utf-8'))
    	print(f"{('P'+str(i).zfill(3)).encode('utf-8')}")
    ser.close()



