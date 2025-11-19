import time as t
import serial as ser

#initial testing to make sure the COM is open
import serial.tools.list_ports as lp
ports = list(lp.comports())
for p in ports:
    print(p.device, p.description)

# Arduino commands: change later with correct strings used in Arduino
forward = 'F'
backward = 'B'
right = 'R'
left = 'L'
stop = 'S'
open_claw = 'O'
close_claw = 'C'
approach = 'A'

# connecting to Arduino
port_num = 'COM7' # change for use
baud_rate = 9600 # change bc i want to make our lives harder

# connect to serial monitor
def connect_to_Arduino(port=port_num, baud=baud_rate):
    for attempt in range(3):
        try:
            arduino = ser.Serial(port, baud, timeout=1)
            t.sleep(2)
            print('Arduino connection on port', port)
            return arduino
        except Exception as ex:
            print(f'Attempt {attempt+1} failed: {ex}')
            t.sleep(1)
    return None
    
# send commands
def send_to_Arduino(arduino, command):
    arduino.write(command.encode()) # string converting string to bytes
    print('sent ' + (command) + 'via serial')
    t.sleep(0.08) # pause (50ms) to process command, can incrase to 0.1?

a = connect_to_Arduino(port_num, baud_rate)
if a is None:
    print("Could not connect to HC-05. Exiting.")
    exit()

# Move forward 10 times
for _ in range(10):
    send_to_Arduino(a, 'F')

# Turn right 10 times
for _ in range(10):
    send_to_Arduino(a, 'R')