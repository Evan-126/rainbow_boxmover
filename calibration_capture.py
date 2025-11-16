# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 16:34:46 2025

@author: carol

This script's code automatically captures calibration frames. 
To calibrate hold checkerboard fully visable in front of the
camera. Press "c" to capture image.

 
"""

import cv2
import os

# create folder to save calibration images if not already exists
folder = "calibration_images"
os.makedirs(folder, exist_ok=True)

# connect to working camera index
cap = cv2.VideoCapture(1)  

count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("Calibration - Press 'c' to capture, 'q' to quit", frame)

    key = cv2.waitKey(1) & 0xFF

    # press 'c' to capture an image
    if key == ord('c'):
        filename = f"{folder}/calib_{count}.jpg"
        cv2.imwrite(filename, frame)
        print(f"Saved {filename}")
        count += 1

    # press 'q' to quit
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
