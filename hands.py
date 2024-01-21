#!/usr/bin/env python3
# Original Author: Antonio X Cerruto, 10-Aug-2022
import mediapipe as mp
import cv2

class HandDetector:
	"""
	HandDetector class detects and tracks hand landmarks in images using
	MediaPipe Hands solution.
	"""
	mp_drawing = mp.solutions.drawing_utils
	mp_hands = mp.solutions.hands
	n_landmarks = 21
	
	def __init__(self,
				model_complexity=0,
				min_detection_confidence=0.5,
				min_tracking_confidence=0.5,
				max_num_hands=1):
		"""
		Arguments:
		model_complexity -- Default 0
		min_detection_confidence -- Default 0.5
		min_tracking_confidence -- Default 0.5
		max_num_hands -- Integer number of hands to detect. Default 1.
		"""
		self.hands = HandDetector.mp_hands.Hands(
					model_complexity=model_complexity,
					min_detection_confidence=min_detection_confidence,
					min_tracking_confidence=min_tracking_confidence,
					max_num_hands=max_num_hands)


	def _process_image(self, img):
		"""
		Function processes input image to detect hands.

		Arguments:
		img -- input image in BGR format

		Returns:
		results -- object containing hand landmarks
		of class 'mediapipe.python.solution_base.SolutionOutputs'
		"""
		# convert to RGB and process image
		img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
		img.flags.writeable = False
		results = self.hands.process(img)
		return results


	def _process_landmarks(self, hand_landmarks):
		"""
		Function processes detected hand_landmarks and returns (x, y)
		pixel coordinates for each hand landmark.

		landmark indices:
		------------------------------------------------
		0 -- WRIST				11 -- MIDDLE_FINGER_DIP
		1 -- THUMB_CMC			12 -- MIDDLE_FINGER_TIP
		2 -- THUMB_MCP			13 -- RING_FINGER_MCP
		3 -- THUMB_IP			14 -- RING_FINGER_PIP
		4 -- THUMB_TIP			15 -- RING_FINGER_DIP
		5 -- INDEX_FINGER_MCP	16 -- RING_FINGER_TIP
		6 -- INDEX_FINGER_PIP	17 -- PINKY_MCP
		7 -- INDEX_FINGER_DIP	18 -- PINKY_PIP
		8 -- INDEX_FINGER_TIP	19 -- PINKY_DIP
		9 -- MIDDLE_FINGER_MCP	20 -- PINKY_TIP
		10 -- MIDDLE_FINGER_PIP

		Arguments:
		hand_landmarks -- object containing hand landmarks

		Returns:
		landmarks -- array of (x, y) pixel coordinates for each hand landmark
		"""
		landmarks = []
		for i in range(self.n_landmarks):
			landmarks.append(
							(hand_landmarks.landmark[i].x,
							hand_landmarks.landmark[i].y))
		return landmarks


	def _extract_cam_data(self, results, img, draw=True):
		"""
		Function processes results of hand detection.

		Arguments:
		results -- object containing hand landmarks
		of class 'mediapipe.python.solution_base.SolutionOutputs'
		img -- input image in BGR format
		draw -- boolean indicating whether to draw landmarks on input image.
		Default True.

		Returns:
		landmarks -- array of (x, y) pixel coordinates for each hand landmark
		for each detected hand
		"""
		landmarks = []
		if results.multi_hand_landmarks:
			for hand_landmarks in results.multi_hand_landmarks:
				if(draw):
					HandDetector.mp_drawing.draw_landmarks(
									img,
									hand_landmarks,
									HandDetector.mp_hands.HAND_CONNECTIONS)
				landmarks.append(self._process_landmarks(hand_landmarks))
		return landmarks


	def get_landmarks(self, img, draw=True):
		"""
		Function that processes input image for hand landmarks
		and optionally draws landmarks on input image.

		Arguments:
		img -- image in BGR format
		draw -- boolean indicating whether to draw landmarks on input image.
		Default True.

		Returns:
		landmarks -- array of (x, y) pixel coordinates for each hand landmark
		for each detected hand
		"""
		results = self._process_image(img)
		landmarks = self._extract_cam_data(results, img, draw)
		return landmarks


	def close(self):
		"""
		Function that closes hand detector.
		"""
		self.hands.close()


# For testing module.
# Executes only if run as a script.
if __name__ == "__main__":
	from camera import Camera

	cam = Camera()
	detect_hands = HandDetector()
	while(True):
		img = cam.get_frame()
		landmarks = detect_hands.get_landmarks(img)
		cam.show(img)
		if(len(landmarks) > 0):
			(x,y) = landmarks[0][8]
			print(f"({x},{y})")
		if cv2.waitKey(5) == ord('q'):
			break



		
		

	

