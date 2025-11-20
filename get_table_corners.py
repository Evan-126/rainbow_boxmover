# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 17:26:21 2025

@author: carol

Helper script to manually capture the four corners of the robot
workspace in the camera feed.
Outputs pixel coordinates of the corners for use in homography mapping (pixel → real-world coordinates).

"""

import cv2

def pick_corners(camera_i=1):

# connect camera
    cap = cv2.VideoCapture(1)
    
    # window for camera
    cv2.namedWindow("Frame")
    corners=[]

    # this function will be called when you click
    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            print(f"Clicked coordinates: ({x}, {y})")
            corners.append((x,y))
    
    # set the mouse callback on the window
    cv2.setMouseCallback("Frame", click_event)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        cv2.imshow("Frame", frame)
        
        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    return corners
