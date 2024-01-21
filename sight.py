#!/usr/bin/env python3
# Created by Antonio X Cerruto 24 Feb 2022
from camera import Camera
import numpy as np
import cv2
import os
import sys
import time

class Sight:
	"Sight class detects and tracks hand landmarks in 3D using two Cameras"
	# parameters for Logitech C615 camera
	a = 120 					# distance in mm between camera midpoints
	w = 62*(np.pi/180)			# camera horizontal viewing angle in radians (adjusted from 78)
								# camera autofocus off and standard (not widescreen) setting enabled
	aspect_ratio = 9/16			# height/width camera aspect ratio
	v = w*aspect_ratio			# camera vertical viewing angle in radians
	beta = (np.pi-w)/2			# blind-area angle on each side of camera
	offset_cbs = 4.87			# distance (mm) from back of camera housing to camera sensor
	offset_cfs = 10.55			# distance (mm) from front of camera housing to camera sensor
	tilt = 0*(np.pi/180)		# camera tilt angle in radians
	h_min = a/2*np.tan(beta-tilt)	# minimum detectable distance by two-camera setup
	# tstart=int(time.time()*1000)

	def __init__(self, l=1, r=2):
		# print(os.getcwd().split(os.sep)[-1])
		self.left_cam_index = l
		self.right_cam_index = r
		self.camL = Camera(self.left_cam_index)		# left camera
		self.camR = Camera(self.right_cam_index)	# right camera
		self.status = 0
		
		# all dimensions in millimeters
		self.x_in4 = 0
		self.y_in4 = 0
		self.z_in4 = 0
		self.x_th4 = 0
		self.y_th4 = 0
		self.z_th4 = 0
		self.grip = 0

		# center angle in degrees measured clockwise from left cam
		self.center_yaw_theta = np.pi/2
		self.center_pitch_theta = np.pi/2

		# output log
		self.f = open('sight.log','w')

	def _update_arr(self, arr, newval):
		newarr = arr.copy()
		newarr.insert(0,newval)
		del newarr[-1]
		return newarr

	def _arc_cot(self, x):
		theta = np.pi/2
		if(x != 0):
			theta = np.arctan(1/x)
			if(theta < 0):
				theta = theta + np.pi
		return theta

	# for calculating horizontal arccot using viewing angle
	# returns angle in radians
	def _get_theta(self, x):
		k = 0.5*np.tan((np.pi-self.w)/2)
		theta = self._arc_cot((0.5-x)/k)
		return theta - self.tilt

	# returns value in millimeters
	def _calculate_depth(self, xL, xR, yL, yR):
		thetaR = self._get_theta(xR)
		thetaL = np.pi-self._get_theta(xL)
		gamma = np.pi-thetaR-thetaL+2*self.tilt
		h = self.a*np.sin(thetaR)*np.sin(thetaL)/np.sin(gamma)
		self.center_yaw_theta = self._arc_cot(0.5*(np.cos(thetaR)/np.sin(thetaR)\
												-np.cos(thetaL)/np.sin(thetaL)))
		return round(h)

	# returns value in millimeters
	def _calculate_x_mm(self, z, theta):
		return round(-z*np.tan(np.pi/2 - theta))

	# returns value in millimeters
	def _calculate_y_mm(self, yL, yR, aspect_ratio, width_mm):
		return round((0.5-(np.mean([yL, yR])))*aspect_ratio*width_mm)

	# _calculate_coords() 
	# coordinates required for inverse kinematics
	# are (x, y, z) in millimeters
	# as defined for robot arm:
	# x --> horizontal on table surface (+right, -left)
	# y --> vertical on table surface (always +)
	# z --> height from table surface (always +)
	#
	# as defined for stereo-camera sight:
	# sensed plane is parallel to camera plane
	# x --> horizontal distance from center of stereo-camera (+right, -left)
	# y --> vertical distance from center of stereo-camera (+above, -below)
	# z --> distance to sensed plane from camera plane
	def _calculate_coords(self):
		# index finger coordinates
		if((self.camL.x_in4 != '' and self.camR.x_in4 != '')):
			# calculate distance to camera (z coordinate) in mm
			self.z_in4 = self._calculate_depth(self.camL.x_in4, self.camR.x_in4, \
													 self.camL.y_in4, self.camR.y_in4)

			# calculate field of view width in mm
			width_mm = 2*(self.z_in4 - self.h_min)*np.tan(self.w/2)

			# calculate x, y coordinates in mm
			self.x_in4 = self._calculate_x_mm(self.z_in4, self.center_yaw_theta)
			self.y_in4 = self._calculate_y_mm(self.camL.y_in4, self.camR.y_in4, self.aspect_ratio, width_mm)
			self.center_pitch_theta = np.pi/2+np.arctan(self.y_in4/self.z_in4)

			# indicate that both hands are visible
			self.status = 1
		else:
			# no hand found in either cam
			if(self.camL.x_in4 == '' and self.camR.x_in4 == ''):
				self.status = 0

			# no hand found in left cam
			elif(self.camL.x_in4 == ''):
				self.status = 0

			# no hand found in right cam
			elif(self.camR.x_in4 == ''):
				self.status = 0

	def run(self):
		self.camL.process_cam_image()
		self.camL.extract_cam_data()
		self.camR.process_cam_image()
		self.camR.extract_cam_data()
		self._calculate_coords()
		self.f.write(f'{self.status},\
			{round(self.center_yaw_theta*180/np.pi)},\
			{round(self.center_pitch_theta*180/np.pi)},\
			{self.x_in4},\
			{self.y_in4},\
			{self.z_in4}\n')
		self.f.flush()

	def run_continuously(self):
		while True:
			self.run()

	def show(self):
		self.camL.show()
		self.camR.show()

		# rearrange windows
		width = 500
		height = round(self.aspect_ratio*width)
		title_left = f'Camera {self.left_cam_index}'
		title_right = f'Camera {self.right_cam_index}'
		cv2.namedWindow(title_left, cv2.WINDOW_NORMAL)
		cv2.resizeWindow(title_left, (width,height))
		cv2.moveWindow(title_left, 0, 0)
		cv2.namedWindow(title_right, cv2.WINDOW_NORMAL)
		cv2.resizeWindow(title_right, (width,height))
		cv2.moveWindow(title_right, width, 0)

	def close(self):
		self.camL.close()
		self.camR.close()

# for testing sight.py module on its own
# execute only if run as a script
if __name__ == "__main__":
	# print("hello")
	s=Sight(0,1) # (left, right)
	while True:
		s.run()
		# s.show()
		# if cv2.waitKey(5) & 0xFF == 27: # Esc key to exit
		  # break
	s.close()



