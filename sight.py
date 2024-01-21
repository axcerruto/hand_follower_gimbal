#!/usr/bin/env python3
# Created by Antonio X Cerruto 21 Jan 2024
from camera import Camera
from hands import HandDetector
from triangulator import Triangulator
import numpy as np
import cv2
import os
import sys
import time

class Sight:
	"Sight class detects and tracks hand landmarks in 3D using two Cameras"

	def __init__(self, l=1, r=2):
		# print(os.getcwd().split(os.sep)[-1])
		self.left_cam_index = l
		self.right_cam_index = r
		self.cam_left = Camera(self.left_cam_index)
		self.cam_right = Camera(self.right_cam_index)
		self.detect_hands_left = HandDetector()
		self.detect_hands_right = HandDetector()
		self.tr = Triangulator(120, 70.3)
		self.status = 0
		
		# coordinates in millimeters
		self.x = 0
		self.y = 0
		self.z = 0

		# angles in radians
		self.yaw = np.pi/2
		self.pitch = np.pi/2

		# output log
		self.f = open('sight.log','w')

	def run(self, show=False):
		coords_left = None
		coords_right = None
		img_left = self.cam_left.get_frame()
		landmarks = self.detect_hands_left.get_landmarks(img_left)
		if(len(landmarks) > 0):
			coords_left = landmarks[0][8]

		img_right = self.cam_right.get_frame()
		landmarks = self.detect_hands_right.get_landmarks(img_right)
		if(len(landmarks) > 0):
			coords_right = landmarks[0][8]

		self.status = 0
		if(coords_left is not None and coords_right is not None):
			self.status = 1
			(x, y, z), (yaw, pitch) = self.tr.pix2mm(coords_left, coords_right)
			print(f"{x}, {y}, {z}, {yaw*180/np.pi}, {pitch*180/np.pi}")
			self.x = x
			self.y = y
			self.z = z
			self.yaw = yaw
			self.pitch = pitch

		self.f.write(f'{self.status},\
			{round(self.yaw*180/np.pi)},\
			{round(self.pitch*180/np.pi)},\
			{self.x},\
			{self.y},\
			{self.z}\n')
		self.f.flush()

		if(show):
			img = cv2.hconcat([img_left, img_right])
			cv2.imshow(f"[left, right] cameras", img)

	def show(self):
		img_left = self.cam_left.get_frame()
		img_right = self.cam_right.get_frame()
		img = cv2.hconcat([img_left, img_right])
		cv2.imshow(f"[left, right] cameras", img)

	def close(self):
		self.cam_left.close()
		self.cam_right.close()

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



