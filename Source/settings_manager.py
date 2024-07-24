import os
import sys

def get_parent_path() -> str: # Get the scripts file path
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.realpath(__file__))
    
# Global Variables
FILE_NAME = os.path.join(get_parent_path(), 'settings.ini')
open(FILE_NAME, 'a')

def change_setting(setting_name, setting_value) -> None: # Add a new setting to settings.ini
    setting_line = None
    setting_value_to_set = f'{setting_name}={setting_value}\n'

    with open(FILE_NAME, 'r') as file:
        # Read all lines into a list
        lines = file.readlines()

    # Iterate through each line in the list
    for line_number, line in enumerate(lines):
        # Check if the setting matches with the one being added
        if line.startswith(setting_name):
            setting_line = line_number
            break

    # If the setting was found, change the value
    if setting_line is not None:
        lines[setting_line] = setting_value_to_set

        # Write the modified setting back to settings.ini
        with open(FILE_NAME, 'w') as file:
            file.writelines(lines)
            return

    # Write the setting to settings.ini
    with open(FILE_NAME, 'a') as file:
        file.write(setting_value_to_set)
        return

def read_setting_value(setting_name) -> str: # Read a value from settings.ini
    with open(FILE_NAME, 'r') as file:
        for line in file:
            if line.startswith(setting_name):
                return line.replace(setting_name + '=', '').strip()
    return None