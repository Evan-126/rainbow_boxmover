# Rainbow_BoxMover
Final Project for ME396P: Python-Controlled Autonmous Robot

Rainbow_BoxMover is a block-sorting robot that integrates computer vision, high-level motion planning, and Arduino-based motor control. An overhead iPhone camera detects the colored blocks and the robot's orientation, while a Python controller plans the robot's path, sends commands to the Arduino, and coordinates pickup and drop-off actions. The system demonstrates end-to-end integration of perception, decision-making, and physical actuation in a small-scale robotic application.


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

* Orientation and distance calculation for navigation
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

### How to Use
1. Ensure Arduino is connected and the correct port is set in port_num
2. Make sure the computer vision camera is connected and streaming (cap)
3. Install dependencies:
    pip install pyserial
4. Run motion planning script:
   python motion_planning_final.py
5. The robot will initialize and attempt to execute the high-level block pick-and-plance routine using the planning logic.

Notes:
* The motion planning routines are designed to work with the Computer Vision module for position   updates.
* Subsystems (CV detction, Arduino communication, and planning logic algorithms) work and are there independently, but full end-to-end testing has not yet been completed.

### Motion Planning Module (Expanded)

The motion planning system orchestrates the full robotics workflow by combining real-time position updates from the Computer Vision module with the discrete motion primitives exposed by the Arduino Control Module.

- It computes navigation goals including target positions, orientations, and approach vectors.  
- It sends single-character commands (`F`, `B`, `L`, `R`, `S`, `A`, `O`, `C`) over serial to the Arduino, each triggering precise, timed motor/servo actions. This command interface supports incremental movement, safe block handling via slow approaches, and coordinated gripper control.  
- The control loop integrates vision feedback and command sequencing to adaptively progress through the block pickup and sorting routine.  
- By abstracting robot actions into fixed-duration primitives, the planning module maintains robust control despite mechanical and communication uncertainties.  
- The discrete command protocol simplifies synchronization between perception, planning, and actuation layers, enabling modular development and testing.

Together, these modules form an end-to-end autonomous system where vision-driven navigation and task execution are tightly coupled with reliable hardware control through a minimal, high-level serial interface.


## Arduino Control Module

The Arduino Control Module implements the low-level motor and servo actuation for the robot, interfaced via Bluetooth serial commands sent from the Python Motion Planning module.

### Overview

This module runs on an Arduino equipped with a dual H-bridge motor driver (e.g., L298N) controlling two DC motors for differential drive, plus a hobby servo for the gripping arm. It receives single-character commands over a software serial Bluetooth connection (HC-05 module) and executes short, timed motor or servo actions.  

The command protocol is simple and stateless: each character corresponds to one discrete motion primitive executed on the robot, e.g., move forward a short burst, turn left, open or close the gripper. After executing the command, the module stops all motors to maintain precise control and prevent unintended drifting.  

This approach enables fine-grained teleoperation and supports higher-level autonomous motion planning driven by continuous feedback from vision and position estimation modules.

### Hardware Interface

| Component | Pins                                  | Description                               |
|-----------|-------------------------------------|-------------------------------------------|
| Motors    | ENA (3), R1 (2), R2 (4), L1 (6), L2 (7), ENB (5) | Dual H-bridge motor driver input pins controlling speed and direction. |
| Servo     | Pin 9                               | PWM pin controlling the servo gripper.    |
| Bluetooth | RX (11), TX (10)                    | HC-05 module connected over SoftwareSerial. |

#### Motion Primitives

| Command | Description                                | Behavior                                 |
|---------|--------------------------------------------|-------------------------------------------|
| `F`     | Forward drive                              | Both motors forward for 100 ms             |
| `B`     | Backward drive                             | Both motors reverse for 100 ms             |
| `L`     | Turn left                                 | Right motor forward pivot for 100 ms      |
| `R`     | Turn right                                | Left motor forward pivot for 100 ms       |
| `S`     | Stop all motors                           | Motors off to halt movement                |
| `A`     | Approach (slow forward)                    | Forward slow for 500 ms (lower speed)      |
| `O`     | Servo open                               | Gripper moves to 0° (open position)       |
| `C`     | Servo close                              | Gripper moves to 80° (closed position)    |

Each motion primitive sets motor direction and enable pins, runs for a fixed delay, then stops motors to keep movements discrete and controlled.

### Command Processing Logic

The Arduino continuously listens for incoming characters on the HC-05 Bluetooth serial port. When a command character is detected, the corresponding motion function is triggered, and a brief movement or servo action is executed before returning to the stop state. This ensures that each command triggers an atomic, timed behavior allowing precise remote control and stepwise autonomous navigation.

### To Run the File

The code used to receive serial commands and interpret them as motion through powering the motors a set amount of time and servos for a set distance is found in the file (`arduinofunctions.ino`). To run this program one would need to download the Arduino IDE, freely available with a quick google search. Additionally, servo and serial test programs are found in the test folder under (`test_scripts/serial_test.py`) and (`test_scripts/servo_test.io`). serial test would be run as a pythono file, but it is a simpler way to show whether or not you've connected to the HC-05. 


---



