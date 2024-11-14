import os
import random
import sys
import time
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController
import keyboard
from PIL import ImageGrab
import pytesseract
from fuzzywuzzy import fuzz
import http.client, urllib
from datetime import datetime

# Tesseract-OCR path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this path if necessary

# Constants
SEARCH_TIME = 16  # Time to wait for search to complete in seconds
CLICK_INTERVAL = 0.5  # Interval between clicks in seconds
DIDNT_FIND_ANYTHING = (1551, 72)  # Coordinates to check for the white pixel
G_CHECK_PIXEL_COORDS = (941, 947)
WHITE_PIXEL = (255, 255, 255)  # RGB values for white

# Item coordinates
ITEM_COORDS = {"pos1": (1024, 422), "pos2": (1114, 422), "pos3": (1200, 422)}
TEXT_BOX_COORDS = {"pos1": (1040, 450, 1200, 470), "pos2": (1140, 450, 1290, 470), "pos3": (1225, 450, 1375, 470)}

# Keywords to collect
KEYWORDS = {
    "Salvaged Hardened Case": ["Hardened", "Case"],
    "Silver Coin": ["Silver", "Coin"],
    "Bronze Coin": ["Bronze", "Coin"],
    "Diamond Ring": ["Diamond", "Ring"],
    "Gold Coin": ["Gold", "Coin"],
    "Go Pro": ["Go", "Pro"],
    "Oyster": ["Oyster"],
    "Scollop Shell": ["Scollop"],
    "Shark Tooth": ["Shark", "Tooth", "35g"]

}

locations = ['pier', 'yacht', 'alamo']


# Initialize controllers
keyboard_controller = KeyboardController()
mouse_controller = MouseController()

random_secs = random.uniform(0.1, 2.3)

# Create directories for debug images if they don't exist
os.makedirs("debug_images/desired_items", exist_ok=True)
os.makedirs("debug_images/initial_detection_screenshot", exist_ok=True)


# def push_notifications(msg_str):
#     conn = http.client.HTTPSConnection("api.pushover.net:443")
#     conn.request("POST", "/1/messages.json",
#                  urllib.parse.urlencode({
#                      "token": "a1x7v8hr7epjf6jzt1hvgchxej71cd",
#                      "user": "um56cd5j8zbzkq2fqwg276tvqpcshr",
#                      "message": f"{msg_str}",
#                  }), { "Content-type": "application/x-www-form-urlencoded" })
#     conn.getresponse()

def get_unique_filename(directory, base_filename, extension):
    filename = f"{base_filename}{extension}"
    full_path = os.path.join(directory, filename)
    dir_photos = os.listdir(directory)

    if len(dir_photos) >= 12:
        for photos in dir_photos:
            delete_path = os.path.join(directory, photos)
            os.remove(delete_path)

    counter = 0
    while os.path.exists(full_path):
        counter += 1
        filename = f"{base_filename}_{counter}{extension}"
        full_path = os.path.join(directory, filename)


    return full_path, counter

def reset_mouse():
    # Get the current position of the mouse
    current_x, current_y = mouse_controller.position
    # Set the new position of the mouse
    mouse_controller.position = (430, 430)
    time.sleep(0.3)
    mouse_controller.position = (current_x, current_y)
    print("mouse reset")

def verify_item_presence(area, keyword):
    # move mouse so old textbox dissapears
    reset_mouse()
    new_screenshot = capture_screenshot()
    text, _ = extract_text_from_area(new_screenshot, area)
    # returns true if our text matches the keyword of the items we are verifying
    return fuzzy_match(text, keyword)

def click_specified_items():
    item_collected = False
    retries = 3  # Limit retries to prevent infinite loops
    time.sleep(1)

    while retries > 0:
        found_any_item = False

        for pos, coords in ITEM_COORDS.items():
            mouse_controller.position = coords
            time.sleep(0.5)  # Small delay to ensure the hover action registers
            item_screenshot = capture_screenshot()  # Take the screenshot after the hover delay
            time.sleep(0.5) #ensure screenshot is ready!!!
            area = TEXT_BOX_COORDS[pos]

            text, cropped_image = extract_text_from_area(item_screenshot, area)

            cropped_image_path, count = get_unique_filename("debug_images/initial_detection_screenshot/", "searches", ".png")
            cropped_image.save(cropped_image_path)
            print(f"Detected text at {pos}: {text}, from photo {count}")

            for item, keywords in KEYWORDS.items():
                if fuzzy_match(text, keywords):
                    found_msg = f"Desired item ({item}) found"
                    print(found_msg)
                    # Check push_notifications for items to notify
                    # notification_items = list(KEYWORDS.keys())[:4]
                    # if item in notification_items:
                    #     push_notifications(found_msg)

                    item_collected = False
                    while True:
                        mouse_controller.position = coords
                        keyboard_controller.press(Key.shift)
                        time.sleep(0.1)
                        mouse_controller.click(Button.left, 1)
                        time.sleep(0.1)
                        keyboard_controller.release(Key.shift)
                        time.sleep(CLICK_INTERVAL)

                        # Verify if the item is still present
                        if not verify_item_presence(area, keywords):
                            print("Item no longer found after clicking, moving to next position...")
                            item_collected = True
                            found_any_item = True
                            break  # Break out of the retry loop to move to the next position
                        else:
                            print("Item still present, retrying click...")
                            reset_mouse()
                            time.sleep(CLICK_INTERVAL)  # Delay before retrying
                    break  # Break the item check loop if item is collected or retrying is done
            if found_any_item:
                break  # Break the outer loop to restart the scanning process

        if not found_any_item:
            print("No more items to collect, exiting the loop.")
            break  # Exit loop if no items were collected in the last pass

        retries -= 1  # Decrement the retry count

    return item_collected
def capture_screenshot():
    # Capture the entire screen
    screenshot = ImageGrab.grab()
    return screenshot

def detect_white_pixel(screenshot, coords, target_color):
    # Get the color of the pixel at the specified coordinates
    pixel_color = screenshot.getpixel(coords)

    # Print the pixel color for debugging
    print(f"Pixel color at {coords}: {pixel_color}")

    # Check if the pixel color matches the target color (white)
    return pixel_color == target_color

def extract_text_from_area(screenshot, area):
    # Crop the screenshot to the area and use Tesseract to extract text
    cropped_image = screenshot.crop(area)
    time.sleep(0.1)
    text = pytesseract.image_to_string(cropped_image)
    return text.strip(), cropped_image

def fuzzy_match(text, keywords, threshold=80):
    for keyword in keywords:
        if fuzz.partial_ratio(text.lower(), keyword.lower()) >= threshold:
            return True
    return False

def simulate_dive():
    print("Simulating dive...")
    # Hold 'shift' and 'w' keys to dive
    centre()
    keyboard_controller.press('w')
    keyboard_controller.press('a')
    centre()
    keyboard_controller.press(Key.shift)
    centre()
    time.sleep(0.5)
    keyboard_controller.release(Key.shift)


def simulate_search():
    time.sleep(0.1)
    print("Starting search...")
    # Press 'g' key to start searching
    keyboard_controller.press('g')

    time.sleep(0.1)
    keyboard_controller.release('g')
    time.sleep(0.1)
    g_fail_screen = capture_screenshot()
    if detect_white_pixel(g_fail_screen, G_CHECK_PIXEL_COORDS, WHITE_PIXEL):
        keyboard_controller.release('w')
        keyboard_controller.release('a')
        print("searching bar appeared")
        time.sleep(SEARCH_TIME)
        screenshot = capture_screenshot()
        print("Screenshot captured, checking for white pixel...")
        if detect_white_pixel(screenshot, DIDNT_FIND_ANYTHING, WHITE_PIXEL):
            print("Did not find anything, restarting the loop.")
            return False
        else:
            print("Search complete and found items")
            return True

    else:
        print('search bar didn’t appear')
        return False


def get_server_restart_status(string):
    # Split the string by spaces
    parts = string.split()

    # Ensure there is at least one part
    if len(parts) < 2:
        raise ValueError("The date time string does not contain enough space-separated values.")

    # Get the first part and the last part
    first_part = " ".join(parts[:-1])  # Join all parts except the last one
    last_part = parts[-1]

    try:
        # Convert the last part to an integer
        last_number = int(last_part)
    except ValueError:
        raise ValueError(f"The last part of date and time '{last_part}' is not a valid integer.")

    # Determine the restart status
    if last_number >= 2:
        status = "PostRestart"
    else:
        status = "PreRestart"

    # Combine the initial part with the status
    return f"{first_part} {status}"


def simulate_coordinate_clicks():
    print("Simulating coordinate clicks...")
    click_specified_items()
    print("Coordinate clicks completed.")

def exit_ui():
    time.sleep(random_secs)
    print("Exiting UI...")
    # Simulate a short 'tab' hold to exit the UI
    keyboard_controller.press(Key.tab)
    time.sleep(0.1)  # Short delay to ensure Tab is registered
    keyboard_controller.release(Key.tab)
    time.sleep(0.25)
    centre()
    print("Exited UI.")

def centre():
    keyboard_controller.press('c')
    time.sleep(0.1)
    keyboard_controller.release('c')

def get_current_datetime():
    # Get the current date and time
    now = datetime.now()

    # Format the date and time as a string
    # You can customize the format string as needed
    formatted_datetime = now.strftime("_%d_%m %H")

    return formatted_datetime

def get_log_file_info(location_index, locations):
    if 0 <= location_index < len(locations):
        location = locations[location_index]
    else:

        location = locations[0]

    date = get_current_datetime()
    file_key = get_server_restart_status(date)
    log_file = f"success_rate_{location}{file_key}.txt"

    return log_file, location

def update_log_counts(log_file, success):
    success_count = 0
    failure_count = 0

    if os.path.exists(log_file):
        with open(log_file, "r") as file:
            lines = file.readlines()
            if len(lines) >= 2:
                try:
                    success_count = int(lines[0].strip())
                    failure_count = int(lines[1].strip())
                except ValueError:
                    # Reset counts if there's an issue with the file
                    success_count = 0
                    failure_count = 0

    if success:
        success_count += 1
    else:
        failure_count += 1

    total = success_count + failure_count
    success_rate = (success_count / total) * 100 if total > 0 else 0

    with open(log_file, "w") as file:
        file.write(f"{success_count} successes\n")
        file.write(f"{failure_count} failures\n")
        file.write(f"Rate {success_rate}")
    return success_count, failure_count, success_rate

def log_result(success=True, location_index=0, locations=None):
    log_file, location_dat = get_log_file_info(location_index, locations)
    success_count, failure_count, success_rate = update_log_counts(log_file, success)
    total = success_count + failure_count
    print(f"Logged following info \n Success Rate: {success_rate:.2f}% ({success_count} successes out of {total} attempts)\n")
def dive_loop(get_location):

    error_count = 0
    found = False
    while not found:
        if simulate_search():
            print('Added search/g count')
            found = True
        else:
            print('Failed to search, diving to attempt research')

            simulate_dive()
            #if error_count >= 2:
            #   exit_ui()
            if error_count >= 5:
                print("failed search 5 times in a row")
            else:
                error_count += 1

    return



def start_diving(get_location):

    while True:
        print("Starting diving automation loop...")
        dive_loop(get_location)
        simulate_coordinate_clicks()
        print("Coordinate clicks completed.")

        # Exit UI
        exit_ui()

        time.sleep(random_secs)


def select_location():
    print("Select a location:")
    for i, loc in enumerate(locations, start=1):
        print(f"{i}: {loc}")

    # Prompt the user to select a location by number
    selection = input("Enter the number corresponding to the location: ")

    # Validate the input and get the corresponding location
    try:
        selection_index = int(selection) - 1
        if 0 <= selection_index < len(locations):

            return selection_index
        else:
            print("Invalid selection. Defaulting to 'location_1'.")
            location = locations[0]
            return location
    except ValueError:
        print("Invalid input. Defaulting to 'location_1'.")
        location = locations[0]
        return location






