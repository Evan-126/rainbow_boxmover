# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 16:28:26 2025

@author: carol
This scripts read the checkerboard images that were 
captured. It detects the corners and computes camera 
matrix and distortion coefficients. Saves results into a file.
"""

import cv2
import numpy as np
import glob

# define checkerboard dimensions (number of internal corners per row and column)
checkerboard_size = (6, 9)  # (columns, rows) - adjust to your printed checkerboard

# pepare object points (0,0,0), (1,0,0), (2,0,0), ... in real-world space
objp = np.zeros((checkerboard_size[0]*checkerboard_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:checkerboard_size[0], 0:checkerboard_size[1]].T.reshape(-1, 2)

# arrays to store object points and image points from all images
objpoints = []  # 3D points in real world
imgpoints = []  # 2D points in image plane

# get list of all calibration images
images = glob.glob("C:/Users/carol/OneDrive/Documents/ME396P/Project/calibration_images/*.jpg")

# print("SEARCH PATH:", r"C:/Users/carol/OneDrive/Documents/ME396P/Project/calibration_images/*.jpg")
# print("Loaded images:", len(images))
# print("Images found:", images)

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # finds the chessboard corners
    ret, corners = cv2.findChessboardCorners(gray, checkerboard_size, None)

    # if found, add object points and refine corner locations
    if ret:
        objpoints.append(objp)
        corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1),
                                    criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
        imgpoints.append(corners2)

        # draw and display corners
        cv2.drawChessboardCorners(img, checkerboard_size, corners2, ret)
        cv2.imshow('Corners', img)
        cv2.waitKey(100)

cv2.destroyAllWindows()

# compute camera calibration
ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

# save the calibration results
np.savez('camera_calib_data.npz', camera_matrix=camera_matrix, dist_coeffs=dist_coeffs)

print("Calibration complete.")
print("Camera matrix:\n", camera_matrix)
print("Distortion coefficients:\n", dist_coeffs)
