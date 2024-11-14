import json
import requests
import uuid
import platform
import hashlib
import os



# #TODO add error handling
# #license_key = input("Please enter your license key: ")

# Data for assigning hardware ID

product_id_paid = "671347741dd59"
product_id = "67133bad0e22b"
license_key = "TRIAL-JMRVJMYZLNFFHSKP"
license_key_PAID = "SHUCK-CWWPQTWHDAAFCSUE"
api_key = "jXMDCU7b8JDGr6F5Tn0wc0uA39KwA6RNoaV3rmRIJtDuOKs9DVVLlCcNfonvpjxD"

def get_hardware_id():
    mac = uuid.getnode()



    plat_id = platform.platform()

    #hash the two id's together

    combined_id = f"{mac} {plat_id}"

    hashed_hardware_id = hashlib.sha256(combined_id.encode()).hexdigest()

    return hashed_hardware_id




def test_shop_api():
    url = "https://dev.sellix.io/v1/self"

    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.request("GET", url, headers=headers)

    print(response.text)

def orders():
    url = "https://dev.sellix.io/v1/orders"

    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.request("GET", url, headers=headers)

    print(response.text)


def extract_productid_licensekey(bot_type):
    filename = f"{bot_type}.txt"
    with open(filename, "r") as file:
        lines = file.readlines()

    # Extract the first and last lines, and strip any surrounding whitespace
    product = lines[0].strip()
    license = lines[-1].strip()

    # Return both the first and last lines
    return product, license




#sets hwid to corrosponding license key
def set_hardware_id(bot_type):

    product, license = extract_productid_licensekey(bot_type)
    print(product)
    url = "https://dev.sellix.io/v1/products/licensing/hardware_id"

    payload = {
        "product_id": product,
        "key": license,
        "hardware_id": get_hardware_id()
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.put(url, json=payload, headers=headers)

    print(f"Set hwid, for following license : {str(response.text)}")

    #now log the HWID into the corrosponding order






def add_hwid(uniqid):


    url = f"https://dev.sellix.io/v1/orders/{uniqid}/custom_fields"

    payload = {"custom_fields": [
        {
            "name": "hwid",
            "value": f"{get_hardware_id()}"
        }
    ]}
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.request("PUT", url, json=payload, headers=headers)

    print(f"Raw Add HWID is {response.text}")

def extract_hwid_uniqid(response_data):
    """
    Extracts the uniqid and hwid from a Sellix API orders response.

    Parameters:
    response_data (dict): The JSON response from the Sellix API containing orders data.

    Returns:
    List of tuples: Each tuple contains the uniqid and hwid (if present), else None for hwid.
    """
    extracted_data = []

    # Loop through all orders in the response
    for order in response_data.get("data", {}).get("orders", []):
        uniqid = order.get("uniqid")
        hwid = None

        # Check if there are custom fields and look for 'hwid'
        for custom_field in order.get("custom_fields", []):
            if custom_field.get("name") == "hwid":
                hwid = custom_field.get("value")
                break

        # Append the uniqid and hwid (could be None if not found)
        extracted_data.append((uniqid, hwid))

    return extracted_data











#check_existing_hwid()

def extract_license_uniqid():



    expired_mock_key = "TRIAL-YNPQENMYVTGWQWEX"
    url = "https://dev.sellix.io/v1/products/licensing/check"

    payload = {
        "product_id": product_id,
        "key": license_key,
        "hardware_id": get_hardware_id()
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Make the request
    response = requests.request("POST", url, json=payload, headers=headers)
    response_text = response.text
    print(f"HTML request made on url : {url} to extract uniqid")
    """
    Extracts the uniqid from a Sellix API license response.

    Parameters:
    response_data (str): The JSON response from the Sellix API containing license data.

    Returns:
    str: The uniqid from the license data.
    """
    # Parse the JSON string
    data = response.json()
    print(f"Raw data response {data}")

    # Extract the uniqid from the license data
    uniqid = data['data']['license']['uniqid']



    return str(uniqid)







def check_license(bot_type):

    product, license = extract_productid_licensekey(bot_type)

    url = "https://dev.sellix.io/v1/products/licensing/check"

    payload = {
            "product_id": product,
            "key": license,
            "hardware_id": get_hardware_id()
        }
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    # Make the request
    response = requests.post(url, json=payload, headers=headers)

    # Try to parse the response as JSON
    try:
        response_log = response.json()
        print(f"Checking license... Raw response: {response_log}")
    except ValueError:
        # If response is not valid JSON, print an error and return False
        print("Invalid response format. Could not parse JSON.")
        return False

    # Handle error based on status code or other error key
    if response_log.get("status") != 200:
        print(f"Error finding license: {response_log.get('error', 'Unknown error')}")
        return False

    # If successful, return True
    return True




#contains functions for getting hwid and checking the hwid against orders from order list
def check_existing_hwid():
    #extracts current user uniqid and passes as the

    uniqid = extract_license_uniqid()
    print(f"UNIQID : {uniqid}")
    add_hwid(uniqid)








    #add logic to check orders list for a matching hwid
    url = "https://dev.sellix.io/v1/orders"

    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.request("GET", url, headers=headers)

    print(response.text)

    hwid_uniqid = response.json()

    print(hwid_uniqid)

#TODO In future update
#check_existing_hwid()



#TODO Launch hwid license check from GUI, if returns true the GUI launches the script



def load_stored_keys():
    stored_keys = {}
    # Ensure the if block is correctly indented inside the function
    if os.path.exists("botmodkeys.txt"):
        with open("botmodkeys.txt", "r") as f:
            for line in f:
                line = line.strip()
                if line and ":" in line:  # Ensure valid lines
                    try:
                        bot_type, key, product_id = line.split(":")
                        stored_keys[bot_type] = (key, product_id)  # Store key and product ID
                    except ValueError:
                        print(f"Skipping improperly formatted line: {line}")
                else:
                    print(f"Skipping invalid or empty line in botmodkeys.txt: {line}")
    else:
        print("botmodkeys.txt not found, add logic to take back to enter key screen.")


    return stored_keys



#Takes the bot type being used and completes a license check. Returns True if successful
def start_hwid_license_check(bot_type):
    set_hardware_id(bot_type)
    # Attempt to check the license
    if not check_license(bot_type):
        # Handle the case where the license check fails
        print("Exiting hwid license check, User must re enter a valid License Key")
        #exits back to main loop
        return False
    else:
        print("Future updates after license check system will check all free trial keys for existing hwid")
        return True

    #how do we stop user from making multiple free trial license keys

    #check_existing_hwid

    #call shucker.start_shucker() from main project
bot = "oyster_shucker"








#user boots up first we check their hwid isnt being used already
#check_existing_hwid()








