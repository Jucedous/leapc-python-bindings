import sys
import os
lib_path = os.path.join(os.path.dirname(__file__), 'dobot-python')
sys.path.append(lib_path)

from lib.interface import Interface
from time import sleep

bot = Interface('/dev/tty.usbmodem14101')

print('Bot status:', 'connected' if bot.connected() else 'not connected')

params = bot.get_arc_params()
print('Params:', params)

# Default start position
bot.set_homing_command(0)
sleep(1)
bot.set_point_to_point_command(8, -30, 0, 0, 0)