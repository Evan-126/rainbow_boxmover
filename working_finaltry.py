import serial
import random as r
import math
import numpy as np
np.random.seed(0) #consistency is key

# from main_computer_vision import 

from collections import defaultdict

from python_motion_planning.common import *
from python_motion_planning.path_planner import *
from python_motion_planning.controller import *

#to turn coordinates with floats to ints
def tgv(coord):
    return int(round(coord[0])), int(round(coord[1]))


## arduino shizzle:
port_num = 'COM7' # change later to correct one
baud_rate = 9600 # change later to correct one

# connect to serial
def connect_to_Arduino(port=port_num, baud=baud_rate, retries=3):
    # tries to connect to Arduino via serial
    # retries up to 'retries' times
    for attempt in range(1, retries + 1):
        try:
            arduino = serial.Serial(port, baud, timeout=1) # timeout->wait time for a response
            time.sleep(2) # initializing
            print(f'Arduino connecton successful on port {port}')
            return arduino
        except Exception as ex:
            print(f'Attempt {attempt} failed: {ex}')
            time.sleep(1)
    print('Could not connect to Arduino after attempts.')
    return None

# send commands
def send_to_Arduino(arduino, command, debug=True):
    # sends a single command to Arduino
    # adds a newline character to ensure proper reading
    # optionally prints command for debugging
    if arduino is not None:
        arduino.write((command + '\n').encode('utf-8')) # string converting string to bytes
        if debug:
            print(f'Sent "{command}" via serial')
        time.sleep(0.02)
    
# functions to turn carolina output into actionable variables

# returns {'color':(x, y), 'color':(x, y), ...}
def block_positions(list_of_positions, distance_threshold=10.0):
    # Flatten input
    flattened_positions = [item for sublist in list_of_positions for item in sublist]

    # Cluster coordinates by color considering spatial proximity
    clusters = {}  # {color: list of clusters}, cluster = list of coords

    for color, coord in flattened_positions:
        if color not in clusters:
            clusters[color] = []

        placed = False
        for cluster in clusters[color]:
            # Check if coord is close enough to cluster members (within threshold)
            if any(math.dist(coord, member) <= distance_threshold for member in cluster):
                cluster.append(coord)
                placed = True
                break
        if not placed:
            # Start new cluster
            clusters[color].append([coord])

    # Compute averages for each cluster
    avg_positions = {}
    for color in clusters:
        for i, cluster in enumerate(clusters[color], 1):
            x_avg = sum(c[0] for c in cluster) / len(cluster)
            y_avg = sum(c[1] for c in cluster) / len(cluster)
            key = f"{color}_{i}" if len(clusters[color]) > 1 else color
            avg_positions[key] = (x_avg, y_avg)

    return avg_positions

#returns (x,y), angle
def robot_position(data):
    yellow_x = []
    yellow_y = []
    red_x = []
    red_y = []

    for i in data:
        yx, yy = i['yellow']['coord']
        rx, ry = i['red']['coord']

        yellow_x.append(yx)
        yellow_y.append(yy)
        red_x.append(rx)
        red_y.append(ry)

        y_x_avg, y_y_avg = sum(yellow_x)/len(yellow_x), sum(yellow_y)/len(yellow_y)
        r_x_avg, r_y_avg = sum(red_x)/len(red_x), sum(red_y)/len(red_y)

        angle = np.arctan2((y_y_avg-r_y_avg), (y_x_avg-r_x_avg))
    return (y_x_avg, y_y_avg), angle


# this is just a list of lists that would come 
# straight out of carolinas code

raw_raw_raw_blocks = [
    [('blue', (14.8, 72.3)), ('green', (67.1, 16.4)), ('orange', (22.6, 38.1)),
     ('blue_1', (75.2, 64.9)), ('green_1', (18.3, 14.7)), ('orange_1', (49.7, 75.8))],

    [('blue', (12.9, 68.6)), ('green', (70.4, 13.5)), ('orange', (28.4, 47.9)),
     ('blue_1', (73.0, 59.1)), ('green_1', (20.1, 22.8)), ('orange_1', (55.8, 73.4))],

    [('blue', (16.5, 74.1)), ('green', (63.9, 18.3)), ('orange', (25.2, 32.7)),
     ('blue_1', (71.4, 66.7)), ('green_1', (14.9, 28.6)), ('orange_1', (45.3, 76.0))],

    [('blue', (20.3, 70.9)), ('green', (68.7, 22.5)), ('orange', (31.7, 35.9)),
     ('blue_1', (74.8, 62.4)), ('green_1', (13.7, 17.9)), ('orange_1', (52.4, 69.8))],

    [('blue', (11.7, 63.2)), ('green', (72.0, 20.1)), ('orange', (23.9, 50.3)),
     ('blue_1', (76.1, 56.8)), ('green_1', (19.0, 33.5)), ('orange_1', (47.8, 72.7))],

    [('blue', (18.6, 75.4)), ('green', (65.3, 11.9)), ('orange', (29.5, 41.2)),
     ('blue_1', (70.2, 68.3)), ('green_1', (16.4, 24.7)), ('orange_1', (54.6, 66.1))]
]


raw_raw_raw_robot = [
    {'yellow': {'pixel': (481, 17), 'coord': (8.603, 2.316)} , 'red': {'pixel': (398, 17), 'coord': (-1.012, 2.290)}},
    {'yellow': {'pixel': (482, 17), 'coord': (8.560, 2.278)}, 'red': {'pixel': (398, 17), 'coord': (-1.071, 2.254)}},
    {'yellow': {'pixel': (481, 18), 'coord': (8.596, 2.305)}, 'red': {'pixel': (398, 17), 'coord': (-1.042, 2.265)}},
    {'yellow': {'pixel': (481, 17), 'coord': (8.550, 2.281)}, 'red': {'pixel': (398, 16), 'coord': (-1.061, 2.279)}},
    {'yellow': {'pixel': (480, 17), 'coord': (8.598, 2.268)}, 'red': {'pixel': (399, 17), 'coord': (-1.032, 2.247)}},
    {'yellow': {'pixel': (481, 17), 'coord': (8.570, 2.298)}, 'red': {'pixel': (398, 18), 'coord': (-1.073, 2.266)}},
    {'yellow': {'pixel': (482, 17), 'coord': (8.585, 2.271)}, 'red': {'pixel': (398, 17), 'coord': (-1.055, 2.258)}}
]

b_pos = block_positions(raw_raw_raw_blocks)

print(b_pos)

r_pos = robot_position(raw_raw_raw_robot)

block_radius = 1.8 # effective radius of the blocks in cm
robot_radius = 9 # effective radius of the robot in cm 

map_ = Grid(bounds=[[0, 86],[0, 86]])
for color, coords in b_pos.items():
    x_idx, y_idx = tgv(coords)
    map_.type_map[x_idx, y_idx] = TYPES.OBSTACLE

map_.inflate_obstacles(radius = (block_radius + robot_radius))
map_.fill_boundary_with_obstacles()

############################################
######    CONTROLLER SECTION ###############
############################################

## note: replace everything to the right of the equals sign 
# with b_pos('color')

print ("position of the block we're chasing: " + str(b_pos["orange_1"]))
random_block = r.choice(list(b_pos.values())) 
end_goal = (random_block[0] - 7.2, random_block[1] - 7.2)

start, goal = tgv(r_pos[0]), tgv(end_goal)
print("start, goal: " + str(start) + str(goal))
map_.type_map[start] = TYPES.START
map_.type_map[goal] = TYPES.GOAL

planner = AStar(map_=map_, start=start, goal=goal)
path, path_info = planner.plan()
# print(path)
# print(path_info)
map_.fill_expands(path_info["expand"])  # for visualizing the expanded nodes

path_world = map_.path_map_to_world(path)
print(path_world)

dim = 2
env = ToySimulator(dim=dim, obstacle_grid=map_, robot_collisions=False)

robots = {
    "1": CircularRobot(dim=dim, radius=1, pose=np.array([5.5, 5.5, 0]), vel=np.zeros(3),
                action_min=np.array([-2, -2, -3.14]), action_max=np.array([2, 2, 3.14]), color="C0", text="1"),
    "2": DiffDriveRobot(dim=dim, radius=1, pose=np.array([5.5, 5.5, 0]), vel=np.zeros(3),
                action_min=np.array([-2.82, 0, -6.28]), action_max=np.array([2.82, 0, 6.28]), color="C1", text="2")
}

controllers = {}
for rid, robot in robots.items():
    obs_space, act_space = env.build_robot_spaces(robot)
    controllers[rid] = PurePursuit(obs_space, act_space, env.dt, path_world, max_lin_speed=3, max_ang_speed=1.9)
    env.add_robot(rid, robot)

obs, _ = env.reset()

vis = Visualizer("Path Visualizer")
vis.render_toy_simulator(env, controllers, steps=300, show_traj=True, show_env_info=True, grid_kwargs={"show_esdf": False})
vis.plot_path(path, style="--", color="C4")
vis.show()

for rid in robots:
    ctrl = controllers[rid]
    print(rid, ":", vis.get_traj_info(rid, ctrl.goal, ctrl.goal_dist_tol, ctrl.goal_orient_tol))
vis.close()

   

#######################################################
####### actually outputting to the robot ##############
####################################################### i like this format of comments lol

# to take the path and turn it into commands!
def path_to_commands(path=path_world, start_pose=r_pos, forward_speed=10 , turn_rate=np.radians(100),  # cm/s and rad/s approx
                     command_duration=0.1, distance_tol=2.0, heading_tol=0.2):
    """
    Converts a path (list of (x,y) waypoints) into discrete commands:
    'forward 0.1s', 'backwards 0.1s', 'left 0.1s', 'right 0.1s'

    Arguments:
    - path: list of (x, y) tuples in world units (e.g., cm)
    - start_pose: (x, y, theta) starting pose of robot
    - forward_speed: approximate forward speed in cm/s
    - turn_rate: approximate angular speed in rad/s
    - command_duration: duration of each discrete command in seconds
    - distance_tol: how close to waypoint to consider it reached (cm)
    - heading_tol: heading error tolerance to decide turning vs moving straight (radians)

    Returns:
    - commands: list of strings (commands) to execute in order
    """

    commands = []

    current_x, current_y, current_theta = start_pose
    
    for waypoint in path:
        wx, wy = waypoint
        
        print (start_pose, waypoint)
        max_iters = 500
        iters = 0
        while True:
            dx = wx - current_x
            dy = wy - current_y
            distance = np.hypot(dx, dy)

            if distance < distance_tol:
                # Waypoint reached
                break

            desired_theta = np.arctan2(dy, dx)
            heading_error = desired_theta - current_theta
            # Normalize heading error to [-pi, pi]
            heading_error = (heading_error + np.pi) % (2 * np.pi) - np.pi

            if abs(heading_error) > heading_tol:
                # Need to turn
                if heading_error > 0:
                    commands.append("L")
                    current_theta += turn_rate * command_duration
                else:
                    commands.append("R")
                    current_theta -= turn_rate * command_duration
                # Normalize current_theta to [-pi, pi]
                current_theta = (current_theta + np.pi) % (2 * np.pi) - np.pi
            else:
                # Move forward
                commands.append("F")
                current_x += forward_speed * command_duration * np.cos(current_theta)
                current_y += forward_speed * command_duration * np.sin(current_theta)
            print(commands)
            iters +=1
            if iters > max_iters:
                print("Max iterations exceeded, breaking to avoid infinite loop.")
                break
    return commands

## finally arduino time !!
# connecting to Arduino
a = connect_to_Arduino(port_num, baud_rate)
rposnew = r_pos[0][0], r_pos[0][1], r_pos[1]
commands = path_to_commands(start_pose = rposnew)
for c in commands:
    send_to_Arduino(a, c)

