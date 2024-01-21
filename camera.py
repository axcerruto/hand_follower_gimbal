#!/usr/bin/env python3
# Created by Antonio X Cerruto 24 Feb 2022
import cv2
import mediapipe as mp
import numpy as np
import sys
import time

class Camera:
	"Camera class detects and tracks hand landmarks"
	mp_drawing = mp.solutions.drawing_utils
	mp_hands = mp.solutions.hands

	def __init__(self, index=0):
		self.index = index
		self.cap = cv2.VideoCapture(self.index)
		self.hands = Camera.mp_hands.Hands(
							model_complexity=0,
							min_detection_confidence=0.5, 
							min_tracking_confidence=0.5, 
							max_num_hands=1)
		self.success, self.image = self.cap.read()
		self.results = self.hands.process(self.image)
		self.x_in4 = 0
		self.y_in4 = 0
		self.x_th4 = 0
		self.y_th4 = 0
		self.grip = 0
		self.tstart = int(time.time()*1000)

		# configure camera capture to MJPG for faster read() operation
		W, H = 1920, 1080
		self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, W)
		self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, H)
		self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
		self.cap.set(cv2.CAP_PROP_FPS, 30)


	def process_cam_image(self, selfie=False):
		# self.tstart = int(time.time()*1000)
		self.success, self.image = self.cap.read()
		# print(f'cap.read(): {int(time.time()*1000)-self.tstart}')

		# self.tstart = int(time.time()*1000)
		if not self.success:
			print("Ignoring empty frame.")
			return
		if(selfie):
			self.image = cv2.cvtColor(cv2.flip(self.image,1), cv2.COLOR_BGR2RGB) #selfie
		else:
			self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
		# print(f'selfie_check: {int(time.time()*1000)-self.tstart}')

		# self.tstart = int(time.time()*1000)
		self.image.flags.writeable = False
		# print(f'image.flags.writeable : {int(time.time()*1000)-self.tstart}')

		# self.tstart = int(time.time()*1000)
		self.results = self.hands.process(self.image)
		# print(f'hands.process(self.image): {int(time.time()*1000)-self.tstart}')

		# self.tstart = int(time.time()*1000)
		self.image.flags.writeable = True
		# print(f'image.flags.writeable: {int(time.time()*1000)-self.tstart}')

		# self.tstart = int(time.time()*1000)
		self.image = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)
		# print(f'cv2.cvtColor: {int(time.time()*1000)-self.tstart}')


	def __process_landmarks__(self, hand_landmarks):
		self.x_in4 = hand_landmarks.landmark[Camera.mp_hands.HandLandmark.INDEX_FINGER_TIP].x
		self.y_in4 = hand_landmarks.landmark[Camera.mp_hands.HandLandmark.INDEX_FINGER_TIP].y
		self.x_th4 = hand_landmarks.landmark[Camera.mp_hands.HandLandmark.THUMB_TIP].x
		self.y_th4 = hand_landmarks.landmark[Camera.mp_hands.HandLandmark.THUMB_TIP].y
		self.grip = int(10+63*(1-np.sqrt((self.x_th4-self.x_in4)**2+(self.y_th4-self.y_in4)**2)))
		if (self.grip > 65):
			self.grip = 90


	def extract_cam_data(self):
		if self.results.multi_hand_landmarks:
			for hand_landmarks in self.results.multi_hand_landmarks:
				Camera.mp_drawing.draw_landmarks(
									self.image, 
									hand_landmarks, 
									Camera.mp_hands.HAND_CONNECTIONS)
				self.__process_landmarks__(hand_landmarks)
		else:
			self.x_in4 = ''
			self.y_in4 = ''
			self.x_th4 = ''
			self.y_th4 = ''
			self.grip = ''


	def run(self, selfie):
		self.process_cam_image(selfie)
		self.extract_cam_data()
		self.show()


	def show(self):
		cv2.imshow(f'Camera {self.index}', self.image)


	def close(self):
		self.hands.close()
		self.cap.release()


	if __name__ == "__main__":
		# execute only if run as a script
		i = int(sys.argv[1])
		print(f'Testing camera module {i}')
		cam = cv2.VideoCapture(i)
		while(True):
			s, image = cam.read()
			cv2.imshow(f'Camera {i}', image)
			if cv2.waitKey(5) & 0xFF == 27: # Esc key to exit
				break



		
		

	

