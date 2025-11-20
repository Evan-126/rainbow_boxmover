#####################################
# second_script.py
#####################################

from evans_computervision import get_current_positions, cap
import time

robot_coords_history = []

print("Starting second script!")

while True:
    robot_dict, angle_deg = get_current_positions()

    if robot_dict is None:
        print("Markers not found. Retrying...")
        time.sleep(0.05)
        continue

    # Extract clean variables
    front_coord = robot_dict['front']['coord']
    back_coord = robot_dict['back']['coord']

    entry = {
        "front": front_coord,
        "back": back_coord,
        "angle": angle_deg,
        "timestamp": time.time()
    }

    robot_coords_history.append(entry)

    print(
        f"Front: {front_coord},  "
        f"Back: {back_coord},  "
        f"Angle: {angle_deg:.1f} deg"
    )

    time.sleep(0.05)   # slow down loop slightly

