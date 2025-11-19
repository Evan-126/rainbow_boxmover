# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 15:15:00 2025

@author: udhak
"""
# most recent 1:36am
import math
import time
import serial
from CV_module import get_updated_frame # replace with actual name

# both in frame, may change if workspace changes
# workspace coordinates
drop_off = (80, 10)
home_location = (10, 10)
color_order = ['orange', 'green', 'blue']

# come back for adjustment
block_to_robotcenter_offset = 8 # cm distance from block to robot center
tolerance_position = 1.5 # cm tolerance for getting to target

# Arduino commands: change later with correct strings used in Arduino
forward = 'F'
backward = 'B'
right = 'R'
left = 'L'
stop = 'S'
open_claw = 'O'
close_claw = 'C'

# connecting to Arduino
port_num = 'COM7' # change later to correct one
baud_rate = 9600 # change later to correct one

# connect to serial monitor
def connect_to_Arduino(port=port_num, baud=baud_rate):
    # try and except to check for connection and for potential fails
    try:
        arduino = serial.Serial(port, baud, timeout=1) # timeout->wait time for a response
        time.sleep(2) # initializing
        print('Arduino connection on port', port)
        return arduino
    except Exception as ex:
        print('Error connecting:', ex)
        return None
    
# send commands
def send_to_Arduino(arduino, command):
    arduino.write((command + '\n').encode('utf-8')) # string converting string to bytes
    time.sleep(0.05) # pause (50ms) to process command, can incrase to 0.1?
    
# ROBOT functions
def calculate_distance(point1, point2):
    # checking how far robot is from a target, point1 and point2 updated dynamically
    
    dist = math.hypot(point2[0] - point1[0], point2[1] - point1[1])
    return dist
 
def calculate_angle(point1, point2):
    # checking which way robot should face to go toward target
    x_dif = point2[0] - point1[0]
    y_dif = point2[1] - point1[1]
    radians = math.atan2(y_dif, x_dif) # arctan formula
    degrees = math.degrees(radians) # Arduino needs degrees
    if degrees < 0:
        degrees += 360 # making angles positive if negative
        
    return degrees

def average_coordinates(coords_list):
    # averages a list of (x,y) coordinates
    if not coords_list:
        return (0,0)
    
    x_sum = sum([c[0] for c in coords_list])
    y_sum = sum([c[1] for c in coords_list])
    n = len(coords_list)
    return (x_sum/n, y_sum/n)

def get_robotcenter_angle(robot_coords_history):
    # returns robot center (front mark) and orientation angle
    # front = center of robot
    # back = used for angle
    
    front_points = [rc['front']['coord'] for rc in robot_coords_history]
    back_points = [rc['back']['coord'] for rc in robot_coords_history]
    
    avg_front = average_coordinates(front_points) # robot center
    avg_back = average_coordinates(back_points)
    
    # robot center is now xactly at front mark
    center_robot = avg_front
    # gets robot's orentation angle (direction it is facing)
    angle = calculate_angle(avg_back, avg_front)
    
    return center_robot, angle # front mark is robot center
 
def calculate_approach_point(block_coords, center_robot, block_to_robotcenter_offset):
    # finds safe point to approach block, a few cm away from block center
    # makes sure robot doesn't push block when moving in
    
    x_dif = block_coords[0] - center_robot[0]
    y_dif = block_coords[1] - center_robot[1]
    distance = math.hypot(x_dif, y_dif)
    if distance == 0:
        return center_robot
    scaling = (distance - block_to_robotcenter_offset)/ distance
    x_approach = center_robot[0] + x_dif * scaling
    y_approach = center_robot[1] + y_dif * scaling
    
    return (x_approach, y_approach)
  
def move_to_target(arduino, center_robot, angle_robot, target_coords):
    # drives robot from current to specific target
    while calculate_distance(center_robot, target_coords) > tolerance_position:
        angle_target = calculate_angle(center_robot, target_coords)
        angle_dif = angle_target - angle_robot
        if angle_dif > 180:
            angle_dif -= 360
        elif angle_dif < -180:
            angle_dif += 360
        
        # turning motion
        if angle_dif > 0:
            send_to_Arduino(arduino, right)
        elif angle_dif < 0:
            send_to_Arduino(arduino, left)
        time.sleep(abs(angle_dif)/90) # turning time, assuming linear turning speed, may need calibration
        send_to_Arduino(arduino, stop)

        send_to_Arduino(arduino, forward)
        time.sleep(0.1)
        send_to_Arduino(arduino, stop)
        
        # update robot position with averaging
        history = []
        for _ in range(3): # take 3 frames to average
            cv_data = get_updated_frame()
            history.append(cv_data['robot_coords']) # make sure same name as CV
            time.sleep(0.02)
        center_robot, angle_robot = get_robotcenter_angle(history)
       
# BLOCK functions
def pickup_block(arduino, center_robot, angle_robot, block_coords):
    # approaching block, opening & closing claw
    approach_coords = calculate_approach_point(block_coords, center_robot, block_to_robotcenter_offset)
    move_to_target(arduino, center_robot, angle_robot, approach_coords)
    move_to_target(arduino, center_robot, angle_robot, block_coords)
    send_to_Arduino(arduino, close_claw)
    time.sleep(0.5)
    
def drop_block(arduino):
    # open claw to release block
    send_to_Arduino(arduino, open_claw)
    time.sleep(0.5)
    
def select_more_blocks(blocks_lst): # list name may be different
    for color_block in color_order:
        for block in blocks_lst:
            if block[0] == color_block:
                return block
    return None

def convert_blocks_from_cv_output(cv_data_history):
    # cv_data_hist: list of CV frames (each with 'blocks_robot_coords)
    # returns averaged block cordiantes list: [(color, (x,y))]
    # takes multiple CV frames & averages positoins for each block color
    
    if not cv_data_history:
        return []
    
    # collect all positions for each color
    color_positions = {}
    for frame in cv_data_history:
        for block in frame['blocks_robot_coords']:
            color, coords = block
            if color not in color_positions:
                color_positions[color] = []
            color_positions[color].append(coords)
    
    # average positions
    blocks_lst = []
    for color, coords_list in color_positions.items():
        avg_coord = average_coordinates(coords_list)
        blocks_lst.append((color, avg_coord))
    return blocks_lst

def one_block_pickup(arduino, center_robot, angle_robot, block):
    # pick up and drop off motion for 1 block
    print(f'Next block: {block[0]} at {block[1]}')
    pickup_block(arduino, center_robot, angle_robot, block[1])
    print(f'Picked {block[0]}')
    move_to_target(arduino, center_robot, angle_robot, drop_off)
    print(f'At drop-off {drop_off}')
    drop_block(arduino)
    print(f'Dropped {block[0]} at drop-off')
    time.sleep(0.5)
    
# maybe don't need it? just goes back to the very starting point
def return_to_home_location(arduino, center_robot, angle_robot):
    # move back to the very start point
    move_to_target(arduino, center_robot, angle_robot, home_location)
    print(f'Returned to starting point {home_location}')
    
def main():
    arduino = connect_to_Arduino()
    if arduino is None:
        return
    print('Motion planning starting.')
    
    # to ensure runs are repeated until no blocks left
    run_finished = False
    while not run_finished:
        # collect multple CV frames for averaging
        robot_history = []
        block_history = []
        for _ in range(3): # take 3 frames per step
            cv_frame = get_updated_frame()
            robot_history.append(cv_frame['robot_coords'])
            block_history.append(cv_frame)
            time.sleep(0.02)
        
        # averaged robot center & angle
        center_robot, angle_robot = get_robotcenter_angle(robot_history)
        
        # averaged block positions
        blocks_lst = convert_blocks_from_cv_output(block_history)
        
        # select next block
        next_block = select_more_blocks(blocks_lst)
       
        if next_block is None:
            print('No blocks left.')
            return_to_home_location(arduino, center_robot, angle_robot)
            print('Run finished.')
            run_finished = True
            break
        
        one_block_pickup(arduino, center_robot, angle_robot, next_block)
        
if __name__ == '__main__':
    main()
       