# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 16:54:52 2025

@author: carol

Script loads camera calibration data to remove lens distortion.
Captures live video feed and detects blocks and deposit zones.
Lastly it uses homography to map the dectected position to the
actual table cordinates in cm.

"""

import cv2
import numpy as np
import pandas as pd

# load saved camera calibration
npzfile = np.load('camera_calib_data.npz')
camera_matrix = npzfile['camera_matrix']
dist_coeffs = npzfile['dist_coeffs']

# connect to the camera (Camo index might be 1)
cap = cv2.VideoCapture(1)



def undistort_frame(frame):
    # remove lens distortion using calibration data
    return cv2.undistort(frame, camera_matrix, dist_coeffs)

def get_largest_contour(contours):
    if len(contours) == 0:
        return None
    return max(contours, key=cv2.contourArea)



def detect_blocks(frame):
    """
    Detect blocks in the frame using color thresholds and contours.
    Returns a list of block centers in pixel coordinates.
    """
    
    # converts the image to HSV for easier color detection
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    block_centers = []
    
    ## dark blue block
    
    # lower_blue = np.array([100, 150, 0])
    # upper_blue = np.array([140, 255, 255])
    # aqua blue
    # lower_blue = np.array([80, 100, 100])
    # upper_blue = np.array([95, 255, 255])
    # mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    # contours, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # for cnt in contours:
    #     M = cv2.moments(cnt)
    #     if M["m00"] != 0:
    #         cx = int(M["m10"]/M["m00"])
    #         cy = int(M["m01"]/M["m00"])
    #         block_centers.append(('blue', (cx, cy))) 
    
    
            
            
    # Yellow block
# Black mask (low V region)
    # lower_black = np.array([0, 0, 0])
    # upper_black = np.array([180, 255, 50])   # adjust 50 → higher/lower depending on lighting
    
    # mask_black = cv2.inRange(hsv, lower_black, upper_black)
    
    # contours, _ = cv2.findContours(mask_black, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # for cnt in contours:
    #     M = cv2.moments(cnt)
    #     if M["m00"] != 0:
    #         cx = int(M["m10"] / M["m00"])
    #         cy = int(M["m01"] / M["m00"])
    #         block_centers.append(('black', (cx, cy)))

    # return block_centers

    
    # MORPH CLEANING KERNEL
    kernel = np.ones((7, 7), np.uint8)

    # -------------------------
    # OMBRE BLUE BLOCK 
    # -------------------------
    lower_blue = np.array([80, 100, 100])
    upper_blue = np.array([95, 255, 255])
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

    mask_blue = cv2.morphologyEx(mask_blue, cv2.MORPH_CLOSE, kernel)
    mask_blue = cv2.morphologyEx(mask_blue, cv2.MORPH_OPEN, kernel)

    contours_blue, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    largest_blue = get_largest_contour(contours_blue)

    if largest_blue is not None:
        M = cv2.moments(largest_blue)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            block_centers.append(('blue', (cx, cy)))

    ### BLACK ###
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 60])

    mask_black = cv2.inRange(hsv, lower_black, upper_black)

    mask_black = cv2.morphologyEx(mask_black, cv2.MORPH_CLOSE, kernel)
    mask_black = cv2.morphologyEx(mask_black, cv2.MORPH_OPEN, kernel)

    contours_black, _ = cv2.findContours(mask_black, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    largest_black = get_largest_contour(contours_black)

    if largest_black is not None:
        M = cv2.moments(largest_black)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            block_centers.append(('black', (cx, cy)))



    ### GREEN ###
    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])
    
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    
    # Erode/dilate to remove noise
    kernel = np.ones((5,5), np.uint8)
    mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_OPEN, kernel)
    mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_CLOSE, kernel)
    
    contours, _ = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 400:   # ignore tiny blobs
            continue
    
        M = cv2.moments(cnt)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            block_centers.append(('green', (cx, cy)))


    ### ORANGE ###
    lower_orange = np.array([5, 120, 120])
    upper_orange = np.array([20, 255, 255])
    mask_orange = cv2.inRange(hsv, lower_orange, upper_orange)
    contours, _ = cv2.findContours(mask_orange, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        M = cv2.moments(cnt)
        if M["m00"] != 0:
            cx = int(M["m10"]/M["m00"])
            cy = int(M["m01"]/M["m00"])
            block_centers.append(('orange', (cx, cy)))
    
    return block_centers

    # # Example: detect red blocks
    # lower_red = np.array([0, 120, 70])
    # upper_red = np.array([10, 255, 255])
    
    # # creates a mask where the red pixels= 1 and everything = 0
    # mask = cv2.inRange(hsv, lower_red, upper_red)
    
    # # finds contours and outlines each detected block
    # contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # block_centers = []
    # calculates the center of each contour. List is being returned.
    # for cnt in contours:
    #     M = cv2.moments(cnt)
    #     if M["m00"] != 0:
    #         cx = int(M["m10"] / M["m00"])
    #         cy = int(M["m01"] / M["m00"])
    #         block_centers.append((cx, cy))
    # return block_centers



'''Pixel to Robot Coordinate Conversion'''

# real-world coordinates in cm (x, y) on table
# example: table is 60cm x 40cm
table_real_coords = np.array([
    [0, 0],      # top-left
    [33, 0],     # top-right
    [33, 37.5],    # bottom-right
    [0, 37.5]      # bottom-left
], dtype=np.float32)

# corresponding pixel coordinates in the camera feed
# you can find these manually by clicking the corners or using a calibration checkerboard
table_pixel_coords = np.array([
    [519, 39],    # pixel of top-left
    [1116, 11],    # pixel of top-right
    [1125, 713],    # pixel of bottom-right
    [490,629 ]     # pixel of bottom-left
], dtype=np.float32)

# compute homography matrix
homography_matrix, status = cv2.findHomography(table_pixel_coords, table_real_coords)

def pixel_to_robot_coords(pixel_point):
    """
    Convert a pixel (x, y) to real-world table coordinates using homography.
    """
    px = np.array([[pixel_point[0], pixel_point[1]]], dtype='float32')
    px = np.array([px])
    real_point = cv2.perspectiveTransform(px, homography_matrix)
    return real_point[0][0]  # returns [X, Y] in cm

# function for motion planning

def get_current_positions(frame=None):
    """
    Returns current positions of blocks and deposit areas in cm
    If no frame is provided, grabs one from camera
    """
    if frame is None:
        ret, frame = cap.read()
        if not ret:
            return [], []
    
    frame_undistorted = undistort_frame(frame)
    blocks = detect_blocks(frame_undistorted)

    # convert to real-world coordinates
    blocks_robot_coords = [(color, pixel_to_robot_coords((x, y))) for color, (x, y) in blocks]

    return blocks_robot_coords


# main loop
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # undistort frame using calibration
    frame_undistorted = undistort_frame(frame)
    
    # detect blocks & deposit areas
    blocks = detect_blocks(frame_undistorted)
    #deposits = detect_deposit_areas(frame_undistorted)
    
    
    for color, (x, y) in blocks:
        # draw block circles for visual feedback (color-coded)
        if color == 'blue':
            cv2.circle(frame_undistorted, (x, y), 10, (255,0,0), -1)  # blue
        elif color == 'black':
            cv2.circle(frame_undistorted, (x, y), 10, (0,255,255), -1)  # yellow    
        elif color == 'green':
            cv2.circle(frame_undistorted, (x, y), 10, (0, 255, 0), -1)  # green
        elif color == 'orange':
            cv2.circle(frame_undistorted, (x, y), 10, (0, 165, 255), -1)  # orange (BGR)

    
    # example inside your main loop
    blocks_robot_coords = [(color, pixel_to_robot_coords((x, y))) for color, (x, y) in blocks]

    # print results
    for color, (rx, ry) in blocks_robot_coords:
        print(f"{color} block: X={rx:.1f} cm, Y={ry:.1f} cm")


    cv2.imshow("Robot Vision", frame_undistorted)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


