import serial
import time
import python_motion_planning as pmp
import math
import numpy as np

# ----------------------------
# 1) Robot and Block Utilities
# ----------------------------
def robot_coords(xf, yf, xb, yb):
    """Return robot center coordinates and heading in radians."""
    robotx = (xf + xb) / 2
    roboty = (yf + yb) / 2
    robotangle = math.atan2(yf - yb, xf - xb)
    return (robotx, roboty, robotangle)

def block_coords():
    """Return dictionary of block positions (x,y)."""
    return {
        'orange1': (13.3, 58.3),
        'orange2': (-9.3, -0.2),
        'green1': (-12.1, 18),
        'green2': (41.2, -31.1)
    }

def obstacle_generator(block_coords, robot_radius=8.0):
    """
    Convert block positions to circular obstacles and inflate by robot radius.
    block_coords: dict of block names -> (x,y)
    robot_radius: inflation radius for robot size
    """
    obs = []
    for pos in block_coords.values():
        x, y = pos
        obs.append((x, y, robot_radius + 1.8))  # (center_x, center_y, bot 'radius' + block 'radius')
    return obs

# 2) Path Smoothing

def chaikin_smooth(path, iterations=3):
    """Basic Chaikin corner-cutting smoothing."""
    path = np.array(path)
    for _ in range(iterations):
        new_path = []
        for i in range(len(path)-1):
            p0 = path[i]
            p1 = path[i+1]
            Q = 0.75*p0 + 0.25*p1
            R = 0.25*p0 + 0.75*p1
            new_path.extend([Q, R])
        path = np.array(new_path)
    return path.tolist()


# 3) Convert Path to Serial Commands

def path_to_serial_commands(path, ser, dt=0.1, forward_speed=0.3, turn_rate=140):
    """
    Convert path [(x,y),...] to discrete 'F', 'L', 'R' commands.
    dt: time per command
    forward_speed: m/s
    turn_rate: deg/s
    """
    current_heading = 0.0  # radians, assume +x start

    for i in range(len(path) - 1):
        x1, y1 = path[i]
        x2, y2 = path[i + 1]

        dx = x2 - x1
        dy = y2 - y1
        desired_heading = math.atan2(dy, dx)

        # Compute smallest turn
        angle_diff = desired_heading - current_heading
        angle_diff = (angle_diff + math.pi) % (2*math.pi) - math.pi

        direction = 'L' if angle_diff > 0 else 'R'
        angle_deg = abs(math.degrees(angle_diff))
        turn_time = angle_deg / turn_rate
        turn_steps = int(turn_time / dt)

        # Send turn commands
        for _ in range(turn_steps):
            ser.write(direction.encode())
            time.sleep(dt)

        current_heading = desired_heading

        # Compute forward steps
        distance = math.hypot(dx, dy)
        forward_time = distance / forward_speed
        forward_steps = int(forward_time / dt)

        # Send forward commands
        for _ in range(forward_steps):
            ser.write(b'F')
            time.sleep(dt)


# 4) Serial Initialization

def serial_init(port="COM6", baud=9600):
    ser = serial.Serial(port, baud, timeout=0.1)
    time.sleep(2)  # wait for HC-05
    return ser


# 5) RRT Planning and Execution

def plan_and_execute():
    # Setup
    robot_start = robot_coords(8, 8, 0, 8)[:2]
    blocks = block_coords()
    first_block = list(blocks.values())[0]

    # Environment
    env = pmp.map(83.8, 86.3)
    obstacles = obstacle_generator(blocks)
    for obs in obstacles:
        env.add_circle(obs[0], obs[1], obs[2])

    # Plan
    planner = pmp.RRT(
        environment=env,
        start=robot_start,
        goal=first_block,
        step_size=10,
        goal_sample_rate=0.1,
        max_iters=5000
    )
    raw_path = planner.plan()
    env.render(path=raw_path)

    # Smooth
    smoothed_path = chaikin_smooth(raw_path, iterations=3)
    env.render(path=smoothed_path)

    # Send commands
    ser = serial_init()
    try:
        path_to_serial_commands(smoothed_path, ser)
    finally:
        ser.close()

# ----------------------------
# Run
# ----------------------------
if __name__ == "__main__":
    plan_and_execute()
