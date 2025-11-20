###############################
# main_computer_vision.py
###############################

import cv2
import numpy as np
import math

###############################################
# CAMERA INITIALIZATION
###############################################

# Change this index to whichever camera works
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise RuntimeError("Could not open camera. Try a different index.")

###############################################
# COLOR RANGES (HSV)
###############################################

yellow_lower = np.array([20, 100, 100])
yellow_upper = np.array([30, 255, 255])

red_lower1 = np.array([0, 100, 100])
red_upper1 = np.array([10, 255, 255])
red_lower2 = np.array([170, 100, 100])
red_upper2 = np.array([180, 255, 255])

###############################################
# PIXEL TO REAL COORDINATE TRANSFORM
###############################################
# Hardcode a simple example for now.
# Replace with your real calibration values.

def px_to_cm(px, py):
    # Example: linear conversion
    X = px * 0.10   # 0.10 cm per pixel
    Y = py * 0.10
    return (X, Y)

###############################################
# HELPER FUNCTION: FIND MARKER CENTER
###############################################

def find_center(mask):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        return None

    largest = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest)

    if area < 100:  # too small => noise
        return None

    M = cv2.moments(largest)
    if M["m00"] == 0:
        return None

    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])

    return (cx, cy)

###############################################
# MAIN DETECTION FUNCTION
###############################################

def detect_robot_markers(frame):
    """
    Returns:
        robot_dict = {
            'front': {'pixel': (px,py), 'coord': (X,Y)},
            'back':  {'pixel': (px,py), 'coord': (X,Y)}
        }
        angle_deg = float
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Yellow mask
    yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
    yellow_pixel = find_center(yellow_mask)

    # Red mask (two ranges)
    red_mask1 = cv2.inRange(hsv, red_lower1, red_upper1)
    red_mask2 = cv2.inRange(hsv, red_lower2, red_upper2)
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)
    red_pixel = find_center(red_mask)

    if yellow_pixel is None or red_pixel is None:
        return None, None

    yellow_coord = px_to_cm(*yellow_pixel)
    red_coord = px_to_cm(*red_pixel)

    # Compute angle (back -> front)
    dy = yellow_coord[1] - red_coord[1]
    dx = yellow_coord[0] - red_coord[0]

    angle_rad = math.atan2(dy, dx)
    angle_deg = math.degrees(angle_rad)
    if angle_deg < 0:
        angle_deg += 360

    robot_dict = {
        "front": {"pixel": yellow_pixel, "coord": yellow_coord},
        "back":  {"pixel": red_pixel,    "coord": red_coord}
    }

    return robot_dict, angle_deg

###############################################
# FUNCTION CALLED BY SECOND SCRIPT
###############################################

def get_current_positions():
    ret, frame = cap.read()
    if not ret:
        return None, None
    return detect_robot_markers(frame)

###############################################
# OPTIONAL: DISPLAY IF RUN ALONE
###############################################

if __name__ == "__main__":
    print("Running main_computer_vision.py standalone. Press Q to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read from camera.")
            break

        robot_dict, angle_deg = detect_robot_markers(frame)

        if robot_dict is not None:
            front_px = robot_dict['front']['pixel']
            back_px = robot_dict['back']['pixel']
            cv2.circle(frame, front_px, 5, (0,255,255), -1)
            cv2.circle(frame, back_px, 5, (0,0,255), -1)

            cv2.putText(frame, f"Angle: {angle_deg:.1f}",
                        (10,30), cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, (255,255,255), 2)

        cv2.imshow("Robot Tracking", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
