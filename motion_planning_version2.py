import pySerial as ser
import python-motion-planning as pmp
import math as m

# wait for ushma and carolina to determine format of data output.
# i willl assume a list of coordinates in a specific order

# block positions come in as a tuple for each block (x,y)
# robot position comes in as dict with {front:(x,y), back:(x,y)}


def robot_coords(xf, yf, xb, yb): # front x, front y, back x, back y
    # goal is to return a robot position and angle absolute to the x-axis
    robotx, roboty = xf, yf
    robotangle = m.atan2((yf-yb)/(xf - xb));
    return robotx, roboty, robotangle

def block_coords 
    ## steal from ushma
    block_coords = # dictionary of block identifiers : (x, y) ## TEST CODE BELOW ###
    # block_coords = {orange1:(13.3, 58.3), orange2:(-9.3, -0.2), green1:(-12.1, 18), green2:(41.2, -31.1)}
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
    
env = pmp.Map(83.8, 86.3)
