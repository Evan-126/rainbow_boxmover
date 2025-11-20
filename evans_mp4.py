"""
Purpose: Average block and robot marker positions over a short window.
Uses precomputed variables `blocks_robot_coords` and `robot_dict` from
the main CV program, without rerunning any CV functions.
"""

import random
import math as m
from collections import defaultdict
import time

# -------------------------
# Example input generator
# -------------------------
def generate_example_window(num_steps=10):
    colors = ['blue', 'green', 'orange']
    blocks_history = []
    robot_history = []

    for _ in range(num_steps):
        # Random block positions
        blocks = [(color, (round(random.uniform(0, 86.3), 1),
                           round(random.uniform(0, 83.8), 1)))
                  for color in colors]
        blocks_history.append(blocks)

        # Random robot markers
        robot_dict = {
            'yellow': {'coord': (round(random.uniform(0, 86.3), 1),
                                 round(random.uniform(0, 83.8), 1))},
            'red': {'coord': (round(random.uniform(0, 86.3), 1),
                              round(random.uniform(0, 83.8), 1))}
        }
        robot_history.append(robot_dict)

    return blocks_history, robot_history

# -------------------------
# History of averaged positions
# -------------------------
robot_coords_history = []

AVERAGE_WINDOW = 0.5  # seconds to average over
SLEEP_TIME = 0.05     # loop sleep time (s)

# -------------------------
# Helper to average blocks
# -------------------------
def average_positions(list_of_positions):
    sums = defaultdict(lambda: [0.0, 0.0])
    counts = defaultdict(int)

    for color, (x, y) in list_of_positions:
        sums[color][0] += x
        sums[color][1] += y
        counts[color] += 1

    avg_positions = {color: (sums[color][0]/counts[color], sums[color][1]/counts[color])
                     for color in sums}
    return avg_positions

# -------------------------
# Helper to average robot markers
# -------------------------
def average_robot_markers(list_of_robot_dicts):
    sums = defaultdict(lambda: [0.0, 0.0])
    counts = defaultdict(int)

    for rd in list_of_robot_dicts:
        if rd is None:
            continue
        for marker, data in rd.items():
            x, y = data['coord']
            sums[marker][0] += x
            sums[marker][1] += y
            counts[marker] += 1

    avg_robot = {marker: (sums[marker][0]/counts[marker], sums[marker][1]/counts[marker])
                 for marker in sums}
    return avg_robot

# -------------------------
# Main averaging loop
# -------------------------
def track_positions(blocks_robot_coords_history, robot_dict_history,
                    average_window=AVERAGE_WINDOW, sleep_time=SLEEP_TIME):
    """
    blocks_robot_coords_history: list of lists of (color, (x, y)) tuples
    robot_dict_history: list of robot_dict snapshots
    """
    start_time = time.time()
    blocks_buffer = []
    robot_buffer = []

    # Collect data for the window
    while time.time() - start_time < average_window:
        # append the latest precomputed CV outputs
        if blocks_robot_coords_history:
            blocks_buffer.extend(blocks_robot_coords_history.pop(0))
        if robot_dict_history:
            robot_buffer.append(robot_dict_history.pop(0))

        time.sleep(sleep_time)

    # Compute averages
    avg_blocks = average_positions(blocks_buffer) if blocks_buffer else {}
    avg_robot  = average_robot_markers(robot_buffer) if robot_buffer else {}

    # Compute robot angle
    if 'yellow' in avg_robot and 'red' in avg_robot:
        yellow_x, yellow_y = avg_robot['yellow']
        red_x, red_y = avg_robot['red']
        angle_deg = m.degrees(m.atan2(yellow_y - red_y, yellow_x - red_x))
    else:
        angle_deg = None

    # Save to history
    entry = {
        "blocks": avg_blocks,
        "robot": avg_robot,
        "angle": angle_deg,
        "timestamp": time.time()
    }
    robot_coords_history.append(entry)

    # Print results
    print(f"Averaged over last {average_window:.2f}s:")
    print("Blocks:")
    for color, (x, y) in avg_blocks.items():
        print(f"  {color}: X={x:.1f} cm, Y={y:.1f} cm")
    if avg_robot:
        print("Robot markers:")
        for marker, (x, y) in avg_robot.items():
            print(f"  {marker}: X={x:.1f} cm, Y={y:.1f} cm")
    if angle_deg is not None:
        print(f"Robot angle: {angle_deg:.1f} deg")
    else:
        print("Robot angle: not detected")
    print("-" * 30)

# -------------------------
# Example usage:
# blocks_robot_coords_history = [...]
# robot_dict_history = [...]
# while True:
#     track_positions(blocks_robot_coords_history, robot_dict_history)

blocks_robot_coords_history, robot_dict_history = generate_example_window()
track_positions(blocks_robot_coords_history, robot_dict_history)

