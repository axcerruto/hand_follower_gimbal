#!/usr/bin/env python3
# Created by Antonio X Cerruto 24 Feb 2022
import numpy as np
import time

class Gimbal:
	"Gimbal class to control two-camera gimbal with adjustable pitch and yaw."
	HEIGHT = 85	# in millimeters

	def __init__(self):
		# gimbal parameters
		self.pitch = 90		# in degrees
		self.yaw = 90		# in degrees
		self.curr_pitch = self.pitch
		self.curr_yaw = self.yaw
		self.x_in4 = 0
		self.y_in4 = 0
		self.z_in4 = 0

	# return time in milliseconds
	def _timestamp_(self):
		return int(time.time()*1000)

	def _bound_angles_(self):
		if(self.pitch >= 180): self.pitch = 180
		if(self.yaw >= 180): self.yaw = 180
		if(self.pitch <= 0): self.pitch = 0
		if(self.yaw <= 0): self.yaw = 0

	def update_angles(self, p, y):
		self.pitch = p
		self.yaw = y
		self._bound_angles_()

	def update_angles_delta(self, p, y):
		self.pitch = self.pitch + p
		self.yaw = self.yaw + y
		self._bound_angles_()

	def move_gimbal(self, ser):
		try:
			ser.write(('P'+str(self.pitch).zfill(3)).encode('utf-8'))
			ser.write(('Y'+str(self.yaw).zfill(3)).encode('utf-8'))
		except:
			print("No serial port found.")

	def move_gimbal_step(self, ser, pitch, yaw):
		try:
			ser.write(('P'+str(pitch).zfill(3)).encode('utf-8'))
			ser.write(('Y'+str(yaw).zfill(3)).encode('utf-8'))
		except:
			print("Error sending data to arm.")

	def update_led_status(self, ser, status):
		try:
			ser.write(('S'+str(status).zfill(3)).encode('utf-8'))
		except:
			print("No serial port found.")

	def read_gimbal(self, ser):
		if(ser.in_waiting > 8):
			line = (ser.readline()).decode('utf-8')
			if(line[0] == 'P'):
				try:
					self.curr_pitch = int(line[1:4])
					self.curr_yaw = int(line[5:-1])
				except:
					pass

	# x, y, z inputs in millimeters
	# pitch, yaw inputs in radians
	# ouputs in millimeters
	def update_coordinates(self, x, y, z):
		if(z != 0):
			pitch = self.curr_pitch*np.pi/180
			yaw = self.curr_yaw*np.pi/180
			alpha_p = np.arctan(y/z)
			h_p = np.sqrt((y)**2+(z)**2)
			self.z_in4 = round(-h_p*np.cos(pitch+alpha_p))+self.HEIGHT

			z_perp = h_p*np.sin(pitch+alpha_p)
			alpha_y = np.arctan(x/z_perp)
			h_y = np.sqrt((x)**2+(z_perp)**2)
			self.x_in4 = round(h_y*np.cos(np.pi-yaw-alpha_y))
			self.y_in4 = round(h_y*np.sin(np.pi-yaw-alpha_y))
			print(f'{self.x_in4}, {self.y_in4}, {self.z_in4}')


# execute only if run as a script
if __name__ == "__main__":
	# for use with Arduino code 'serial_read.ino'
	import serialport
	ser = serialport.port_setup()
	gimbal = Gimbal()
	target_y = 180
	target_p = 180
	t_write = gimbal._timestamp_()
	t_read = gimbal._timestamp_()
	while True:
		if(gimbal._timestamp_()-t_write > 35): # 30us works well
			gimbal.update_angles(target_p, target_y)
			gimbal.move_gimbal(ser)
			t_write=gimbal._timestamp_()

		if(gimbal._timestamp_()-t_read > 1):
			gimbal.read_gimbal(ser)
			print(f'target_y: {target_y}, current_y: {gimbal.curr_yaw}')
			if(gimbal.curr_yaw <= 0):
				target_y = 180
			elif(gimbal.curr_yaw >= 180):
				target_y = 0
			if(gimbal.curr_pitch >= 180):
				target_p = 0
			elif(gimbal.curr_pitch <= 0):
				target_p = 180
			t_read=gimbal._timestamp_()


