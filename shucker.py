import time
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController
import keyboard


keyboard_controller = KeyboardController()
start = False



def realistic_drag(start, end, duration=1.0):
    """
    Clicks and drags from the start coordinate to the end coordinate in a realistic manner.

    :param start: Tuple (x, y) for the starting coordinate.
    :param end: Tuple (x, y) for the ending coordinate.
    :param duration: Time in seconds to complete the drag action.
    """
    mouse = MouseController()

    # Get the current position of the mouse
    start_x, start_y = start
    end_x, end_y = end

    # Move to the starting point and click
    mouse.position = (start_x, start_y)
    mouse.press(Button.left)

    # Calculate the number of steps and time interval between each step
    steps = 50  # Number of steps for the drag action
    interval = duration / steps  # Time between each step

    for step in range(steps):
        # Calculate intermediate position
        intermediate_x = start_x + (end_x - start_x) * step / steps
        intermediate_y = start_y + (end_y - start_y) * step / steps
        mouse.position = (intermediate_x, intermediate_y)
        time.sleep(interval)

    # Ensure the mouse ends at the final position
    mouse.position = (end_x, end_y)
    time.sleep(interval)  # Small pause before releasing the button

    # Release the mouse button
    mouse.release(Button.left)

def perform_special_actions():
    """
    Simulates pressing 'Tab', 'W', 'S', and 'Tab' again with 1-second intervals between each key press.
    """
    keyboard_controller.press(Key.tab)
    time.sleep(0.1)  # Short delay to ensure Tab is registered
    keyboard_controller.release(Key.tab)
    keyboard_controller.press("w")
    time.sleep(0.5)
    keyboard_controller.release("w")
    time.sleep(0.1)
    keyboard_controller.press("s")
    time.sleep(0.5)
    keyboard_controller.release("s")
    time.sleep(1)
    keyboard_controller.press(Key.tab)
    time.sleep(0.1)
    keyboard_controller.release(Key.tab)

    time.sleep(0.1)

def main_loop(start, end, num_loops=500, wait_time=11):
    """
    Runs the dragging action in a loop with a wait time in between each loop.
    Every 100 loops, it performs special actions (Tab, W, S, Tab) with 1-second gaps.

    :param start: Tuple (x, y) for the starting coordinate.
    :param end: Tuple (x, y) for the ending coordinate.
    :param num_loops: Number of times to repeat the drag action.
    :param wait_time: Time in seconds to wait between each loop.
    """
    for i in range(1, num_loops + 1):
        realistic_drag(start, end, duration=1)  # Adjust the duration as needed
        time.sleep(wait_time)

        # Every 100 loops, perform special actions
        if i % 50 == 0:
            perform_special_actions()

def start_shucker():

    while not keyboard.is_pressed("esc"):  # Corrected syntax
        start_coord = (620, 420)
        end_coord = (720, 420)
        num_loops = 251  # You can adjust this as needed
        wait_time = 11
        main_loop(start_coord, end_coord, num_loops, wait_time)












