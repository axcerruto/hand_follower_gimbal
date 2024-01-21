#!/usr/bin/env python3
# Original Author: Antonio X Cerruto, 10-Aug-2022
import numpy as np

class Triangulator:
	"""
	Triangulator class converts from pixels to millimeters for
	x, y, z dimensions (width, height, depth) on a stereocamera.

	(+) positive millimeters above camera center
	(-) negative millimeters below camera center

	(+) positive millimeters right of camera center
	(-) negative millimeters left of camera center

			(+)
	(-)	[left, right]	(+)
			(-)
	"""

	def __init__(self,
		inter_axial_distance,
		viewing_angle,
		aspect_ratio = 9/16,
		offset_cam_front = 0):
		"""
		Arguments:
		inter_axial_distance -- distance in millimeters between camera lenses
		viewing_angle -- viewing angle in degrees for each camera
		aspect_ratio -- height/width aspect ratio for each camera
		(default 9/16)
		offset_cam_front -- distance in millimeters from front of camera
		housing to camera sensor (default 0)
		"""
		self.a = inter_axial_distance
		self.w = viewing_angle * (np.pi/180)
		self.aspect_ratio = aspect_ratio
		self.offset_cfs = offset_cam_front
		self.beta = (np.pi-self.w)/2
		self.h_min = self.a/2 * np.tan(self.beta)


	def _arccot(self, x):
		"""
		Function calculates the inverse cotangent.
		Returns value in radians.

		Arguments:
		x -- input value

		Returns:
		angle -- angle in radians
		"""
		angle = np.pi/2
		if(x != 0):
			angle = np.arctan(1/x)
			if(angle < 0):
				angle += np.pi
		return angle


	def _get_theta(self, x, viewangle):
		"""
		Function converts a pixel value to angle in radians
		relative to zero pixel position

		Arguments:
		x -- horizonal pixel value normalized to [0, 1]
		viewangle -- viewing angle in radians

		Returns:
		theta -- horizontal angle in radians relative to left camera edge
		"""
		k = 0.5 * np.tan((np.pi-viewangle)/2)
		theta = self._arccot((0.5-x)/k)
		return theta


	def _pix2mm_z(self, coords_left, coords_right):
		"""
		Function takes as input the coordinates of a point seen on left
		and right cameras in pixel values, and outputs the z cordinate
		of that point in millimeters.
		Input coordinates expected as normalized pixel values, so that each
		value is between 0 and 1. Coordinates are referenced to the top left
		corner of the frame, which is (0,0).

		Arguments:
		coords_left -- (xl, yl) coordinates for point on left camera
		in normalized pixel values [0, 1]
		coords_right -- (xr, yr) coordinates for point on right camera
		in normalized pixel values [0, 1]

		Returns:
		z -- depth in millimeters from stereocam center
		of point defined by input coordinates
		yaw -- angle in radians referenced to stereocam vertical centerplane
		of point defined by input coordinates
		"""
		(xl, yl) = coords_left
		(xr, yr) = coords_right
		theta_r = self._get_theta(xr, self.w)
		theta_l = np.pi - self._get_theta(xl, self.w)
		gamma = np.pi - theta_r - theta_l
		h = self.a * np.sin(theta_r) * np.sin(theta_l) / np.sin(gamma)
		yaw = self._arccot(0.5*(np.cos(theta_r)/np.sin(theta_r)\
								-np.cos(theta_l)/np.sin(theta_l)))
		z = round(h - self.offset_cfs)
		return z, yaw


	def _pix2mm_y(self, yl, yr, z):
		"""
		Function takes as input the coordinates of a point seen on left
		and right cameras in pixel values, the depth of that point
		in millimeters,
		and outputs the y cordinate of that point in millimeters.
		Input coordinates expected as normalized pixel values, so that each
		value is between 0 and 1. Coordinates are referenced to the top left
		corner of the frame, which is (0,0).

		Arguments:
		yl -- y coordinate for point on left camera
		in normalized pixel values [0, 1]
		yr -- y coordinate for point on right camera
		in normalized pixel values [0, 1]
		z -- depth in millimeters from stereocam center
		of point defined by input coordinates

		Returns:
		y -- vertical distance in millimeters from stereocam center
		of point defined by input coordinates
		pitch -- angle in radians referenced to stereocam horizontal
		centerplane of point defined by input coordinates
		"""
		pitch = self._get_theta(np.mean([yl, yr]), self.w * self.aspect_ratio)
		pitch = np.pi/2 - pitch
		y = round(z * np.tan(pitch))
		return y, pitch


	def _pix2mm_x(self, z, angle):
		"""
		Function takes as input the coordinates of a point seen on left
		and right cameras in pixel values, and outputs the x cordinate
		of that point in millimeters.
		Input coordinates expected as normalized pixel values, so that each
		value is between 0 and 1. Coordinates are referenced to the top left
		corner of the frame, which is (0,0).

		Arguments:
		z -- depth in millimeters from stereocam center
		of point defined by input coordinates
		angle -- angle in radians referenced to stereocam vertical centerplane
		of point defined by input coordinates

		Returns:
		x -- horizontal distance in millimeters from stereocam center
		of point defined by input coordinates
		"""
		x = round(-z/np.tan(angle))
		return x


	def pix2mm(self, coords_left, coords_right):
		"""
		Function takes as input the coordinates of a point seen on left
		and right cameras in pixel values, and outputs the cordinates
		of that point in millimeters.
		Input coordinates expected as normalized pixel values, so that each
		value is between 0 and 1. Pixel coordinates are referenced to the
		top left corner of the frame, which is (0,0).

		Arguments:
		coords_left: (xl, yl) -- coordinates for point on left camera
		in normalized pixel values [0, 1]
		coords_right: (xr, yr) -- coordinates for point on right camera
		in normalized pixel values [0, 1]

		Returns:
		(x, y, z), (yaw, pitch)
		(x, y, z) -- coordinates in millimeters of point defined by input
		coordinates, referenced to stereocamera center
		(yaw, pitch) -- angles in radians referenced to stereocamera center
		"""
		(xl, yl) = coords_left
		(xr, yr) = coords_right
		z, yaw = self._pix2mm_z((xl, yl), (xr, yr))
		x = self._pix2mm_x(z, yaw)
		y, pitch = self._pix2mm_y(yl, yr, z)
		return (x, y, z), (yaw, pitch)


# For testing module.
# Executes only if run as a script.
if __name__ == "__main__":
	from camera import Camera
	from hands import HandDetector
	import cv2

	tr = Triangulator(120, 70.3)
	cam_left = Camera(1)
	cam_right = Camera(0)
	detect_hands_left = HandDetector()
	detect_hands_right = HandDetector()
	while True:
		coords_left = None
		coords_right = None
		img_left = cam_left.get_frame()
		landmarks = detect_hands_left.get_landmarks(img_left)
		if(len(landmarks) > 0):
			coords_left = landmarks[0][8]

		img_right = cam_right.get_frame()
		landmarks = detect_hands_right.get_landmarks(img_right)
		if(len(landmarks) > 0):
			coords_right = landmarks[0][8]

		img = cv2.hconcat([img_left, img_right])
		cv2.imshow(f"[left, right] cameras", img)

		if(coords_left is not None and coords_right is not None):
			(x, y, z),_ = tr.pix2mm(coords_left, coords_right)
			print(f"{x}, {y}, {z}")

		if cv2.waitKey(5) == ord('q'):
			break
	cam_left.close()
	cam_right.close()
