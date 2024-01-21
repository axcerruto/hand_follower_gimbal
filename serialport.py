#!/usr/bin/env python3
# Created by Antonio X Cerruto 24 Feb 2022
import glob
import serial

#BAUDRATE=115200
BAUDRATE=250000

def port_setup():
	try:
		# list arduino ports: /dev/tty.usbmodem*
		port = glob.glob('/dev/tty.usbserial*')[0]			# get port
		ser = serial.Serial(port, BAUDRATE, rtscts=True, timeout=0.005)	# open serial port
		print(ser.name) 						# check which port was really used
		ser.reset_input_buffer()
		ser.reset_output_buffer()
	except:
		print("ERROR: no port found /dev/tty.usbserial*")
	return ser

def read_state():
	port = glob.glob('/dev/tty.usbserial*')[0]
	with serial.Serial(port, BAUDRATE, rtscts=True) as ser:
		line = ser.readline()
		print(line)
	return

def main():
	ser = port_setup()	# set up port
	ser.write(b'56\n')
	ser.close()			# close port
	return

if __name__ == "__main__":
    # execute only if run as a script
    main()
    # read_state()



