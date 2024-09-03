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

def signal_handler(sig, frame):
    global running
    print("Exiting...")
    running = False

def main():
    global running
    my_listener = MyListener()

    connection = leap.Connection()
    connection.add_listener(my_listener)

    running = True
    
    bot = Interface('/dev/tty.usbmodem14101')
    signal.signal(signal.SIGINT, signal_handler)

    with connection.open():
        bot.set_homing_command(0)
        sleep(1)
        while running:
            if my_listener.fist_detected:
                # Move the robot to the home position if a fist is detected
                bot.set_homing_command(0)
            elif my_listener.hand_detected:
                # Retrieve the changes in coordinates
                delta_x, delta_y, delta_z = my_listener.change_x, my_listener.change_y, my_listener.change_z
                # Apply the coefficient
                delta_x, delta_y, delta_z = delta_x * 0.3, delta_y * 0.3, delta_z * 0.3
                # Move the robot based on the change in hand position
                bot.set_point_to_point_command(8, delta_x, delta_y, delta_z, 0)
            else:
                # Move the robot to a default position if no hand is detected
                bot.set_point_to_point_command(8, 0, 0, 0, 0)
            sleep(0.1)  # Add a delay to avoid rapid looping
if __name__ == "__main__":
    main()