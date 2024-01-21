#!/usr/bin/env python3
# Original Author: Antonio X Cerruto, 10-Aug-2022
import cv2
import platform

if(platform.system().lower() == 'linux'):
	try:
		import jetson_utils
	except ImportError:
		print("IMPORT ERROR: jetson_utils not imported.")


class Camera:
	"""
	Camera class opens a camera on MacOS, Windows, or Linux.
	Optionally uses jeton_utils on NVIDIA Jetson.
	"""
	def __init__(self,
				index=0,
				jetson=False,
	 			selfie=False,
	 			fps=None,
				W=None,
				H=None,
	 			MJPG=True):
		"""
		Arguments:
		index -- integer index for camera input
		jetson -- Boolean to use jetson_utils. Default False.
		selfie -- Boolean to mirror camera capture. Default False.
		fps -- integer to optionally set frames per second.
		W -- integer to optionally set frame width.
		H -- integer to optionally set frame height.
		MJPG -- Boolean to configure camera capture to MJPG. Default True.
		"""
		self.index = index
		self.jetson = False
		self.selfie = selfie

		if(platform.system().lower() == 'linux'
		and jetson == True):
			self.cap = jetson_utils.videoSource(f'/dev/video{index}')
			self.jetson = jetson
		else:
			self.cap = cv2.VideoCapture(index)

			if(W is not None and H is not None):
				self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, W)
				self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, H)

			if(fps is not None):
				self.cap.set(cv2.CAP_PROP_FPS, fps)

			# configure camera capture to MJPG for faster read
			if(MJPG):
				self.cap.set(cv2.CAP_PROP_FOURCC,
							cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))


	def get_frame(self):
		"""
		Function that updates camera frame and returns bgr image.

		Arguments:
		None

		Returns:
		img -- image in BGR format
		"""
		img = None
		if(self.jetson):
			try:
				# format options: 'rgb8', 'rgba8', 'rgb32f', 'rgba32f'
				img_cuda = self.cap.Capture(format='rgb8')
				bgr_img = jetson_utils.cudaAllocMapped(
										width=img_cuda.width,
										height=img_cuda.height,
										format='bgr8')
				jetson_utils.cudaConvertColor(img_cuda, bgr_img)
				jetson_utils.cudaDeviceSynchronize()
				img = jetson_utils.cudaToNumpy(bgr_img)
			except:
				print("WARNING: Ignoring empty frame.")
				return img
		else:
			success, img = self.cap.read()
			if(not success):
				print("WARNING: Ignoring empty frame.")
				return img
		if(self.selfie):
			img = cv2.flip(img,1)
		return img


	def show(self, img):
		"""
		Function that displays input image.

		Arguments:
		img -- image in BGR format

		Returns:
		None
		"""
		cv2.imshow(f"Cam {self.index}", img)


	def run(self):
		"""
		Function that updates camera frame and displays it.
		"""
		img = self.get_frame()
		if(img is not None):
			self.show(img)


	def close(self):
		"""
		Function that releases camera capture.
		"""
		self.cap.release()

# For testing module.
# Executes only if run as a script.
if __name__ == "__main__":
	cam = Camera(0, selfie=False)
	while(True):
		cam.run()
		if(cv2.waitKey(5) == ord('q')):
			break
