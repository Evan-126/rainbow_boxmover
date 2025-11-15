# motion planning
import serial
import math
import time

# need Arduino setup
arduino = serial.Serial('COM', 9600) # COM & baud will be different
time.sleep(2) # initializing Arduino

# calibration
dis_to_time = 50 # moving 1 cm --> 50ms motor time (test and change)
turn_to_time = 10 # 1 degree --> 10ms motor time
slow_approach = 0.5 # slow down when approaching block

# send to Arduino
def send_to_Arduino(command):
    arduino.write((command + '\n').encode()) # send command string
    print('Sent:', command) # just to test for debugging
    time.sleep(0.1) # time for Arduino to process
    
# robot coordinates: state tracking --> robot's knowledge of where it is on table
x_robot = 0
y_robot = 0
angle_robot = 0

# camera coordinates --> robot coordinates
def camera_to_robot(x_cam, y_cam, height_pic, x_scale=1, y_scale=1, x_offset=0, y_offset=0):
    """
    Converts camera coordinates to robot coordiantes
    x_cam, y_cam: coordinates of detected block from camera
    height_pic: height of picure in pixels
    x_scale, y_scale: scaling pixels to cm
    x_offset, y_offset = offset relative to camera
    
    """
    x_table = x_cam * x_scale + x_offset
    y_table = (height_pic - y_cam) * y_scale + y_offset # flip y for robot
    return x_table, y_table

# calculating distance to move & angle to turn
# x_estimate & y_estimate = target location relative to current location
# y = forward, x = left or right
def calculate_movement(x_estimate, y_estimate):
    global x_robot, y_robot, angle_robot # getting robot's current state
    
    move_x = x_estimate - x_robot # how much robot moves in x
    move_y = y_estimate - y_robot # how much robot moves in y
    
    # distance formula
    distance = math.sqrt(move_x ** 2 + move_y ** 2)
    
    # angle for turn
    angle_turn = math.atan2(move_x, move_y) # in radians
    angle = math.degrees(angle_turn) # convert to degrees for Arduino
    
    # turn angle relative to current angle
    req_turn = angle - angle_robot
    req_turn = (req_turn + 180) % 360 - 180 # normalizing to -180 to 180 so turn is not drastic
    
    return req_turn, distance

# moving to the correct location
def moving_to_block(x_estimate, y_estimate):
    global x_robot, y_robot, angle_robot 
    
    req_angle, distance = calculate_movement(x_estimate, y_estimate)
    # sending turning signal
    send_to_Arduino(f'TURN {int(req_angle)}')
    angle_robot = (angle_robot + req_angle) % 360
    
    # when getting close to block
    if distance < 10:
        # if distance to block is < 10, slow down as approaching
        distance *= slow_approach
    
    # moving forward
    send_to_Arduino(f'FORWARD {int(distance)}')
    x_robot = x_estimate
    y_robot = y_estimate
    # to test
    print(f'Robot moved ({x_robot:.1f}, {y_robot:.1f}), facing {angle_robot:.1f} deg')
    
# at location now need to pickup the block
def pickup_block(x_block, y_block, x_deposit, y_deposit):
    # move to block
    moving_to_block(x_block, y_block)
    
    # grab block
    send_to_Arduino('PICK')
    time.sleep(0.5) # time to pickup
    
    # move to deposit area
    moving_to_block(x_deposit, y_deposit)
    
    # drop in deposit
    send_to_Arduino('RELEASE')
    time.sleep(0.5)
    
# picking up blocks in rainbow order

order = {'red': 1, 'orange': 2, 'yellow': 3, 'green': 4, 'blue': 5, 'purple': 6}

def sort_color(blocks):
    sort_blocks = sorted(blocks, key=lambda b: order[b['color']])
    
    return sort_blocks


def pickup_order(blocks, x_deposit_area, y_deposit_area, spacing=10):
    # x & y deposit_area = top left of deposit area
    blocks_ordered = sort_color(blocks)
    
    deposit_place = 0 # deposit box for each block
    
    for block in blocks_ordered:
        x_block = block['x']
        y_block = block['y']
        
        # to test
        print(f'Grabbing {block["color"]} block at ({x_block}, {y_block}')
        
        # deposit for this particular block
        deposit_x = x_deposit_area + deposit_place * spacing
        deposit_y = y_deposit_area
        
        # pickup & deposit
        pickup_block(x_block, y_block, deposit_x, deposit_y)
        
        deposit_place += 1
        


# adjust if robot is going away from path
def fix_path(x_current, y_current, x_estimate, y_estimate):
    
    pass
    

def main():
    pass


if __name__ == '__main__':
    main()

