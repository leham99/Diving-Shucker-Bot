import customtkinter as ctk
import os
import time
import threading
import keyboard
from shucker import start_shucker
from divingbot import start_diving

import authentication

SELLIX_API_URL = "https://dev.sellix.io/v1/licenses/validate"
SELLIX_API_KEY = "jXMDCU7b8JDGr6F5Tn0wc0uA39KwA6RNoaV3rmRIJtDuOKs9DVVLlCcNfonvpjxD"

class UI_Manager:
    def __init__(self, root):
        self.root = root
        self.root.title("BotMod [FiveM Script Manager]")
        self.root.geometry("600x600")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.valid_license_keys = {"diving_bot": "ABC123", "oyster_shucker": "XYZ789"}
        self.diving_bot_buttons_visible = False
        self.shucker_buttons_visible = False

        self.create_widgets()

    def create_widgets(self):
        # Add "Welcome to BotMod" at the top
        welcome_label = ctk.CTkLabel(self.root, text="Welcome to BotMod", font=("Arial", 24, "bold"))
        welcome_label.pack(pady=20)

        # Diving Bot Section
        diving_frame = ctk.CTkFrame(self.root, corner_radius=10)
        diving_frame.pack(padx=15, pady=15, fill="both", expand=True)

        ctk.CTkLabel(diving_frame, text="Diving Bot", font=("Arial", 18, "bold")).pack(pady=10)

        self.btn_show_diving_license = ctk.CTkButton(diving_frame, text="Select Diving Bot", command=lambda: self.handle_license_check("diving_bot"), width=200, height=50, font=("Arial", 14))
        self.btn_show_diving_license.pack(pady=20)

        # Oyster Shucker Section
        shucker_frame = ctk.CTkFrame(self.root, corner_radius=10)
        shucker_frame.pack(padx=15, pady=15, fill="both", expand=True)

        ctk.CTkLabel(shucker_frame, text="Oyster Shucker", font=("Arial", 18, "bold")).pack(pady=10)

        self.btn_show_shucker_license = ctk.CTkButton(shucker_frame, text="Select Oyster Shucker", command=lambda: self.handle_license_check("oyster_shucker"), width=200, height=50, font=("Arial", 14))
        self.btn_show_shucker_license.pack(pady=20)

        # Buttons that will be shown after license validation (initially hidden)
        self.diving_start_stop_frame = ctk.CTkFrame(diving_frame, corner_radius=10)
        self.shucker_start_stop_frame = ctk.CTkFrame(shucker_frame, corner_radius=10)



    def launch_bot_screen(self, bot_name):
        keybind = "z"
        print(f"Attempting to open launch window for {bot_name}")

        # Create a new CTkToplevel window for the bot launch screen
        self.launch_bot_window = ctk.CTkToplevel(self.root)
        self.launch_bot_window.title(f"Press {keybind} to launch {bot_name}")
        self.launch_bot_window.geometry("800x500")

        # Ensure the window is centered on the main application window
        x_position = self.root.winfo_x() + (self.root.winfo_width() // 2) - 150
        y_position = self.root.winfo_y() + (self.root.winfo_height() // 2) - 75
        self.launch_bot_window.geometry(f"400x200+{x_position}+{y_position}")

        # Add a label with the launch instruction
        label = ctk.CTkLabel(self.launch_bot_window, text=f"Press {keybind} to activate {bot_name} and esc to exit.", font=("Arial", 14))

        label.pack(pady=20)

        # Keep the window on top of others
        self.launch_bot_window.lift()
        self.launch_bot_window.attributes('-topmost', True)





    def handle_license_check(self,bot_name):

            if authentication.start_hwid_license_check(bot_name):
                print(f"license check valid: Launching {bot_name}")
                self.launch_bot_screen(bot_name)






            #TODO handle bot name to launch correct bot




            # Start a separate thread for the bot program and key listening
                def bot_thread():
                    if bot_name == "diving_bot":
                        print("Starting Diving Bot Thread...")
                        target_function = start_diving
                    elif bot_name == "oyster_shucker":
                        print("Starting Oyster Shucke Thread...")
                        target_function = start_shucker
                    else:
                        print(f"Unknown bot name: {bot_name}")
                        return  # Exit if the bot name is invalid

                    while True:
                        if keyboard.is_pressed("z"):
                            print(f"Launching {bot_name} program...")
                            target_function()  # Call the appropriate function
                            break
                        time.sleep(0.1)  # Prevent high CPU usage in the loop

                    # Run the bot thread in the background
                threading.Thread(target=bot_thread, daemon=True).start()


            else:
                #if fails program will prompt you to enter key
                self.enter_license_prompt(bot_name)



    def enter_license_prompt(self, bot_name):
        #add new window
        self.license_prompt_window = ctk.CTkToplevel(self.root)
        #access title method
        self.license_prompt_window.title(f"Enter license key for {bot_name}")
        #set size
        self.license_prompt_window.geometry("300x150")


        #set text for window by passing the window as root arg
        ctk.CTkLabel(self.license_prompt_window, text="Enter License Key:", font=("Arial", 12)).pack(pady=10)
        #STORES the license entry
        self.license_key_entry = ctk.CTkEntry(self.license_prompt_window, width=200)
        self.license_key_entry.pack(pady=10)

        #validate btn which validates the
        ctk.CTkButton(
            self.license_prompt_window,
            text="Validate",
            command=lambda: self.validate_and_retry(bot_name)
        ).pack(pady=5)

        self.license_prompt_window.lift()
        self.license_prompt_window.attributes('-topmost', True)
        self.license_prompt_window.after_idle(lambda: self.license_prompt_window.attributes('-topmost', False))



    def validate_and_retry(self, bot_name):
        # Get the license key entered by the user
        entered_license_key = self.license_key_entry.get()

        # Store the license key (your existing store_key function)
        self.store_key(entered_license_key, bot_name)

        # Close the license prompt window
        self.license_prompt_window.destroy()

        # Retry the license check
        self.handle_license_check(bot_name)







    def store_key(self, key, bot_type):
                filename = f"{bot_type}.txt"
                with open(filename, "a") as f:
                    f.write(f"{key}\n")








    def show_diving_bot_controls(self):
        if not self.diving_bot_buttons_visible:
            self.diving_start_stop_frame.pack(pady=10)
            ctk.CTkButton(self.diving_start_stop_frame, text="Start Diving Bot", command=self.print_diving_bot_directory).pack(pady=5)
            ctk.CTkButton(self.diving_start_stop_frame, text="Stop Diving Bot", command=self.print_stop_diving_bot_directory).pack(pady=5)
            self.diving_bot_buttons_visible = True

    def show_shucker_controls(self):
        if not self.shucker_buttons_visible:
            self.shucker_start_stop_frame.pack(pady=10)
            ctk.CTkButton(self.shucker_start_stop_frame, text="Start Oyster Shucker", command=self.print_oyster_shucker_directory).pack(pady=5)
            ctk.CTkButton(self.shucker_start_stop_frame, text="Stop Oyster Shucker", command=self.print_stop_oyster_shucker_directory).pack(pady=5)
            self.shucker_buttons_visible = True

    # Directory printing functions for testing
    def print_diving_bot_directory(self):
        print(f"Diving Bot Script Path: {os.path.join(os.getcwd(), 'scripts', 'diving_bot.py')}")

    def print_stop_diving_bot_directory(self):
        print("Stop Diving Bot")

    def print_oyster_shucker_directory(self):
        print(f"Oyster Shucker Script Path: {os.path.join(os.getcwd(), 'scripts', 'oyster_shucker.py')}")

    def print_stop_oyster_shucker_directory(self):
        print("Stop Oyster Shucker")

if __name__ == "__main__":
    root = ctk.CTk()
    app = UI_Manager(root)
    root.mainloop()
