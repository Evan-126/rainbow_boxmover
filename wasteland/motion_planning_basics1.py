import math
import numpy as np
import python_motion_planning as pmp


width, height = 83.3, 86.8

# ----------------------------
# 1) Robot and Block Utilities
# ----------------------------
ROBOT_RADIUS = 8.0  # in same units as your map

def robot_coords(xf, yf, xb, yb):
    robotx = (xf + xb) / 2
    roboty = (yf + yb) / 2
    robotangle = math.atan2(yf - yb, xf - xb)
    return (robotx, roboty, robotangle)

def block_coords():
    return {
        'orange1': (13.3, 58.3),
        'orange2': (-9.3, -0.2),
        'green1': (-12.1, 18),
        'green2': (41.2, -31.1)
    }

def obstacle_generator(block_coords, robot_radius=ROBOT_RADIUS):
    """Return list of (x, y, radius) obstacles."""
    obs = []
    for pos in block_coords.values():
        x, y = pos
        obs.append((x, y, robot_radius + 1.8))  # inflate for robot size
    return obs

# ----------------------------
# 2) Path Smoothing (Chaikin)
# ----------------------------
def chaikin_smooth(path, iterations=3):
    path = np.array(path)
    for _ in range(iterations):
        new_path = []
        for i in range(len(path) - 1):
            p0 = path[i]
            p1 = path[i + 1]
            Q = 0.75 * p0 + 0.25 * p1
            R = 0.25 * p0 + 0.75 * p1
            new_path.extend([Q, R])
        path = np.array(new_path)
    return path.tolist()

# ----------------------------
# 3) Differential Drive Commands
# ----------------------------
def diff_drive_steps(angle_diff, distance, wheel_base=15.0, wheel_speed=0.3, turn_rate=140, dt=0.1):
    """Return number of steps for turning and moving."""
    angle_deg = abs(math.degrees(angle_diff))
    direction = 'L' if angle_diff > 0 else 'R'
    turn_time = angle_deg / turn_rate
    turn_steps = max(1, int(turn_time / dt))
    forward_time = distance / wheel_speed
    forward_steps = max(1, int(forward_time / dt))
    return turn_steps, direction, forward_steps

def path_to_commands(path, dt=0.1, forward_speed=0.3, turn_rate=140, wheel_base=15.0):
    """Convert a list of (x,y) path points to ['F','L','R'] commands."""
    current_heading = 0.0
    commands = []

    for i in range(len(path) - 1):
        x1, y1 = path[i]
        x2, y2 = path[i + 1]

        dx = x2 - x1
        dy = y2 - y1
        desired_heading = math.atan2(dy, dx)
        angle_diff = (desired_heading - current_heading + math.pi) % (2 * math.pi) - math.pi
        distance = math.hypot(dx, dy)

        turn_steps, direction, forward_steps = diff_drive_steps(
            angle_diff, distance, wheel_base, forward_speed, turn_rate, dt
        )

        commands.extend([direction] * turn_steps)
        commands.extend(['F'] * forward_steps)
        current_heading = desired_heading

    return commands

# ----------------------------
# 4) Motion Planning Simulation
# ----------------------------
def plan_and_simulate():
    robot_start = robot_coords(8, 8, 0, 8)[:2]
    blocks = block_coords()
    first_block = list(blocks.values())[0]

    # Create high-resolution environment
    env = pmp.env.ToySimulator(width, height)  # units match your coordinate system

    # Add obstacles as circles
    for (x, y, r) in obstacle_generator(blocks):
        env.add_circle(x, y, r)

    # Plan path using RRT
    planner = pmp.RRT(
        environment=env,
        start=robot_start,
        goal=first_block,
        step_size=5,
        goal_sample_rate=0.1,
        max_iters=5000
    )

    raw_path = planner.plan()
    smoothed_path = chaikin_smooth(raw_path, iterations=3)

    # Render paths
    env.render(path=raw_path, wait=True)
    env.render(path=smoothed_path, wait=True)

    # Generate differential drive commands
    commands = path_to_commands(smoothed_path)
    return commands

# ----------------------------
# Run simulation
# ----------------------------
if __name__ == "__main__":
    commands = plan_and_simulate()
    print("Simulated robot commands (first 200):", commands[:200])
    print("Total commands:", len(commands))
