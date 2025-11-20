import serial
import time as t
import pmp
import math as m

# wait for ushma and carolina to determine format of data output.
# i willl assume a list of coordinates in a specific order

# block positions come in as a tuple for each block (x,y)
# robot position comes in as dict with {front:(x,y), back:(x,y)}

robot_starting_position = [8,8,0,8]
# block_starting_positions = {orange1}

def serial_init():
    PORT = "COM7"
    BAUD = 9600   # Must match HC-05 + Arduino Serial baud rate

    ser = serial.Serial(PORT, BAUD, timeout=0.1)
    t.sleep(2)                 # Give the HC-05/Arduino a moment to settle

    try:
        while True:
            ch = 
            ser.write(ch.encode())   # Send 1 character
            print("Sent:", ch)
            t.sleep(0.1)          # 100 ms
    finally:
        ser.close()

def robot_coords(xf, yf, xb, yb): # front x, front y, back x, back y
    # goal is to return a robot position and angle absolute to the x-axis
    robotx, roboty = xf, yf
    robotangle = m.atan2((yf-yb)/(xf - xb));
    return robotx, roboty, robotangle

def block_coords(dict=None):
    ## steal from ushma
    # block_coords = # dictionary of block identifiers : (x, y) ## TEST CODE BELOW ###
    block_coords = {orange1:(13.3, 58.3), orange2:(-9.3, -0.2), green1:(-12.1, 18), green2:(41.2, -31.1)}
    return block_coords

def obstacle_generator(block_coords):
    obs = []
    for block in block_coords:
        ob_circ = list(block).append(m.sqrt(2)*(1.4/2.54)) 
        # turn block coords (center of block) into circle of radius of outside of block
        # lil math bit in there is finding max distance on a face, using 1.4 because all blocks are filleted.
        new_ob_circ = ob_circ[0:1].append(ob_circ[2] + 8)
        # inflate the obstacles by half the diagonal of the robot
        obs.append(new_ob_circ) 
        # note that this weird name came from our lightning talk!! shoutout us from last months fr
    env.update(obs)
    return obs

def path_to_serial_commands(
        path,
        ser,
        dt=0.1,
        forward_speed=0.2,     # m/s
        turn_rate=90           # deg/s
    ):

### with the purpose of converting the path to serial commands ###
### required: had to test straight out speed and turn speed of robot

    # Current heading of robot (radians). Assume starting facing +x direction.
    current_heading = 0.0

    # Loop over each path segment
    for i in range(len(path) - 1):
        x1, y1 = path[i]
        x2, y2 = path[i + 1]

        # ------------------------------
        # 1) Compute desired heading
        # ------------------------------
        dx = x2 - x1
        dy = y2 - y1
        desired_heading = m.atan2(dy, dx)

        # ------------------------------
        # 2) Compute smallest turn angle
        # ------------------------------
        angle_diff = desired_heading - current_heading

        # Normalize to [-pi, pi]
        angle_diff = (angle_diff + m.pi) % (2*math.pi) - math.pi

        # Determine turn direction
        direction = 'L' if angle_diff > 0 else 'R'
        angle_deg = abs(m.degrees(angle_diff))

        # How many seconds does the turn take?
        turn_time = angle_deg / turn_rate
        turn_steps = int(turn_time / dt)

        # ------------------------------
        # Send 'L' or 'R' commands
        # ------------------------------
        for _ in range(turn_steps):
            ser.write(direction.encode())
            time.sleep(dt)

        # Update heading
        current_heading = desired_heading

        # ------------------------------
        # 3) Compute forward distance/time
        # ------------------------------
        distance = math.hypot(dx, dy)
        forward_time = distance / forward_speed
        forward_steps = int(forward_time / dt)

        # ------------------------------
        # Send 'F' commands
        # ------------------------------
        for _ in range(forward_steps):
            ser.write(b'F')
            time.sleep(dt)
#curve smoothing options (untested)
# def chaikin_smooth(path, iterations=3):
#     """
#     Chaikin corner-cutting smoothing.
#     Produces a C1-continuous path (smooth, no sharp corners).
#     """
#     path = np.array(path)
#     for _ in range(iterations):
#         new_path = []
#         for i in range(len(path)-1):
#             p0 = path[i]
#             p1 = path[i+1]
#             Q = 0.75*p0 + 0.25*p1
#             R = 0.25*p0 + 0.75*p1
#             new_path.extend([Q, R])
#         path = np.array(new_path)
#     return path.tolist()

# def curvature(p_prev, p, p_next):
#     """
#     Compute curvature from three consecutive points.
#     Curvature k = angle change / arc length.
#     """
#     a = np.linalg.norm(p - p_prev)
#     b = np.linalg.norm(p_next - p)
#     if a < 1e-6 or b < 1e-6:
#         return 0
    
#     v1 = (p - p_prev) / a
#     v2 = (p_next - p) / b
#     angle = np.arccos(np.clip(np.dot(v1, v2), -1, 1))
    
#     return angle / ((a + b) / 2)

# def curvature_limited_smooth(path, max_curvature, iterations=3):
#     """
#     Smooths the path but rejects any smoothing that causes curvature too high
#     (i.e., robot would need an impossible turn).
#     """
#     path = np.array(path)
    
#     for _ in range(iterations):
#         new_path = []
#         for i in range(len(path)-1):
#             p0 = path[i]
#             p1 = path[i+1]
#             Q = 0.75*p0 + 0.25*p1
#             R = 0.25*p0 + 0.75*p1
            
#             # Check curvature with neighbors
#             if len(new_path) > 0:
#                 p_prev = np.array(new_path[-1])
#                 if curvature(p_prev, Q, R) > max_curvature:
#                     # Skip smoothing for this segment
#                     new_path.append(p0.tolist())
#                     continue
            
#             new_path.extend([Q, R])
        
#         path = np.array(new_path)
    
#     return path.tolist()

# def obstacle_aware_smooth(path, is_free_fn, iterations=3, samples=5):
#     """
#     Path smoothing that avoids obstacles by checking line segment clearance.
#     - is_free_fn(x,y) must return True if free, False if collision.
#     - samples: number of samples to check along each smoothed segment.
#     """
#     path = np.array(path)
    
#     def segment_clear(a, b):
#         for s in np.linspace(0, 1, samples):
#             x = a[0]*(1-s) + b[0]*s
#             y = a[1]*(1-s) + b[1]*s
#             if not is_free_fn(x, y):
#                 return False
#         return True
    
#     for _ in range(iterations):
#         new_path = []
#         for i in range(len(path)-1):
#             p0 = path[i]
#             p1 = path[i+1]
            
#             # Proposed smoothed points
#             Q = 0.75*p0 + 0.25*p1
#             R = 0.25*p0 + 0.75*p1
            
#             # Must not collide
#             if segment_clear(p0, Q) and segment_clear(Q, R) and segment_clear(R, p1):
#                 new_path.extend([Q, R])
#             else:
#                 # Keep original geometry if smoothing unsafe
#                 new_path.append(p0)
        
#         new_path.append(path[-1])
#         path = np.array(new_path)
    
#     return path.tolist()

# # MASTER FUNCTION YOU CALL
# def smooth_path(path, max_curvature=None, obstacle_check_fn=None, iterations=3):
#     """
#     Unified smoothing entry point.
    
#     path: list of (x,y) nodes from RRT
#     max_curvature: if given, enforces robot turn limits
#     obstacle_check_fn: if given, prevents smoothing into obstacles
#     iterations: number of smoothing passes
    
#     Behavior:
#       - If obstacle_check_fn is provided → obstacle-aware smoothing
#       - Else if max_curvature is provided → curvature-limited smoothing
#       - Else → simple Chaikin smoothing
#     """
#     if obstacle_check_fn is not None:
#         return obstacle_aware_smooth(path, obstacle_check_fn, iterations)
#     elif max_curvature is not None:
#         return curvature_limited_smooth(path, max_curvature, iterations)
#     else:
#         return chaikin_smooth(path, iterations)
    
env = pmp.Map(83.8, 86.3)

first_block = list(block_coords().values())[0]

robo_cord = robot_coords(8,8,0,8)

planner = pmp.RRT(
    environment=env,
    start=(robo_cord), 
    goal=(first_block),
    step_size=10,
    goal_sample_rate=0.1,
    max_iters=5000
)

path = planner.plan()

env.render(path=path)

# smoothed_path = pmp.smooth_path(
#     path, 
#     max_curvature=1.2
#     obstacle_check_fn=my_map.is_free,
#     iterations=4
# env.render(path=smoothed_path)

commands = pmp.path_to_commands(
    path, 
    dt=0.1
    forward_speed=0.2
    turn_rate=90
)

