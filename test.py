import leap
import time
import sys
import os
import signal
lib_path = os.path.join(os.path.dirname(__file__), 'dobot-python')
sys.path.append(lib_path)
from lib.interface import Interface
from my_listener import MyListener

from time import sleep

latest_command = None
execute_flag = False  # Flag to indicate when to execute the command

# Global threshold for coordinate difference
COORDINATE_THRESHOLD = 2

# Function to receive new commands
def receive_command(new_command):
    global latest_command, execute_flag
    latest_command = new_command  # Store the new command
    execute_flag = True  # Set flag to execute the new command

def signal_handler(sig, frame):
    global running
    print("Exiting...")
    running = False

def main():
    global running, bot
    my_listener = MyListener()
    latest_coordinates = [0, 0, 0, 0]
    homing_executed = False
    prev_thumb_index_flag = -1

    connection = leap.Connection()
    connection.add_listener(my_listener)

    running = True
    
    bot = Interface('/dev/tty.usbmodem14101')
    signal.signal(signal.SIGINT, signal_handler)


    
    with connection.open():
        bot.set_homing_command(0)
        sleep(1)
        pose = bot.get_pose()

        # Convert the first four elements of the pose to integers
        running_coordinates = [int(value) for value in pose[0:4]]
        while running:
            if my_listener.fist_detected:
                if not homing_executed:
                    # Move the robot to the home position if a fist is detected for the first time
                    bot.set_homing_command(0)
                    homing_executed = True
                    running_coordinates = [275, 0, 85 , 0]
            elif my_listener.hand_detected:
                delta_x, delta_y, delta_z, rotation, gripper = my_listener.prev_x, my_listener.prev_y, my_listener.prev_z, my_listener.prev_yaw, my_listener.thumb_index_flag
                delta_x, delta_y, delta_z, rotation = int(-delta_z * 0.4), int(-delta_x * 0.4), int(delta_y * 0.4), int(rotation * 1)
                x,y,z,r = bot.get_pose()[0:4]
                if (latest_coordinates != [delta_x, delta_y, delta_z, rotation] and
                    abs(running_coordinates[0] - int(x)) <= COORDINATE_THRESHOLD and
                    abs(running_coordinates[1] - int(y)) <= COORDINATE_THRESHOLD and
                    abs(running_coordinates[2] - int(z)) <= COORDINATE_THRESHOLD and
                    abs(running_coordinates[3] - int(r)) <= COORDINATE_THRESHOLD):
                    latest_coordinates = [delta_x, delta_y, delta_z, rotation]
                    running_coordinates = [275 + delta_x, 0 + delta_y, 85 + delta_z, rotation]
                    bot.set_point_to_point_command(2, *running_coordinates)
                
                if (prev_thumb_index_flag != gripper):
                    prev_thumb_index_flag = gripper
                    if gripper == 1:
                        bot.set_end_effector_gripper(False, False)
                    elif gripper == 0:
                        bot.set_end_effector_gripper(True, True)
                    elif gripper == 2:
                        bot.set_end_effector_gripper(True, False)
                homing_executed = False
            else:
                # Move the robot to a default position if no hand is detected
                latest_coordinates = [0, 0, 0]
                # bot.set_point_to_point_command(8, *latest_coordinates, 0)
    
if __name__ == "__main__":
    main()