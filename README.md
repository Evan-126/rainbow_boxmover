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

* Multiple checkerboard images are captured from different angles.
* Corner points are detected and matched to known 3D locations.
* `cv2.calibrateCamera()` computes:
  * The **camera intrinsic matrix**
  * **Lens distortion coefficients**
* These parameters are saved and later applied to undistort each incoming frame.

#### 2. Table Corner Selection (Homography Setup)

Before running object detection, the user must manually click the four corners of the table/bounds in the camera view in the following order:

1. Top-left
2. Top-right
3. Bottom-right
4. Bottom-left

These pixel coordinates are paired with measured table dimensions to compute the homography matrix, enabling conversion from pixel to real-world (x, y) coordinates in centimeters.


### Dependencies

* Python 3
* OpenCV
* NumPy
* Camo Camera app (for virtual webcam)
