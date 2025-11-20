# rainbow_boxmover
Final Project for ME396P: python-based autonomous arduino-run robot. Heavy use of Computer vision and Motion Planning



## Camera Vision Module

The Camera Vision system provides real-time detection of blocks and robot markers using an overhead camera. It functions as the robot’s vision system, delivering accurate workspace coordinates to the Motion Planning module.

### Overview

* Overhead camera captures the entire robot workspace in real time using the **Camo Camera** app.
* Frames are undistorted using pre-computed **camera calibration parameters**.
* Color segmentation (HSV masking + morphological filtering) is used to detect:
  * Colored blocks (green, orange, and blue)
  * Robot orientation markers (yellow + red)
* Pixel positions are converted to real-world table coordinates (cm) using a homography matrix.
* The module provides continuous updates so the motion planner can:
  * Track the robot’s position
  * Identify block positions
  * Plan and execute movements in real time

### Key Features

* Live video capture with distortion removal
* Robust color-based object detection
* Automatic extraction of (x, y) table coordinates
* Real-time visualization of detections (triangles + circle markers)
  
### Calibration & Corner Selection Workflow

Accurate coordinate mapping requires two calibration steps:

#### 1. Camera Calibration (Checkerboard Images)

A helper script (`calibration_capture.py`) is included to collect checkerboard photos:
* Opens the live camera feed; Press **c** to capture a frame  **q** to quit  
* Saves all frames to `/calibration_images/`
Captured images from multiple angles are used to detect corner points and match them to known 3D locations. (`compute_calibration.py`)  computes the camera intrinsic matrix and lens distortion coefficients, which are saved and later applied to undistort each frame.

#### 2. Table Corner Selection (Homography Setup)

Before running object detection, the user must manually click the four corners of the table/bounds in the camera view in the following order:

1. Top-left
2. Top-right
3. Bottom-right
4. Bottom-left

These pixel coordinates are paired with measured table dimensions to compute the homography matrix, enabling conversion from pixel to real-world (x, y) coordinates in centimeters.


## Motion Planning Module

This module implements the high-level navigation and task logic for the block-sorting robot. It determines how the robot should orient, move, approach blocks, pick them up, and transport them to the drop-off zone. The module communicates with the Arduino for motor and claw control while using computer-vision updates to track the robot's position and orientation.

### Overview

The motion planning system coordinates three main tasks:
1. Navigation:
   Computes angles, distances, and turn coorrections to guide the robot toward targets.
2. Block Handling:
   Selects blocks based on a priority color order and generates approach points to ensure safe      pickup.
3. Integrated Control Loop:
   Continuously updates robot position from computer vision, averages multiple frames for           stability, and sends serial commands to the Arduino to adjust the robot's movement in real       time.

### Key Features

* Orientatio and distance calculation for navigation
* Automatic alignment to target coordinates
* Slow-apprach behavior when near a block
* Averaging of multiple CV frames for smoother tracking
* Safe approach-point generation to prevent bumping blocks
* Block selection based on predefined color priority (orange--green--blue)
* Pickup and drop-off routines (claw control + movement)
* Optional return-to-home behavior after completing all blocks
* Serial communication with Arduino for motor commands

### Dependencies

* Python 3
* math
* time
* serial (pySerial)
* Computer Vision module
* * get_current_positions()
  * detect_robot_markers()
  * cap camera stream
  

## Arduino Control Module
--- insert info @evan


