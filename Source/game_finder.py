import os
import vdf
from settings_manager import change_setting, read_setting_value

def check_if_scp_path_is_valid(file_path):
    file_path = os.path.abspath(file_path)
    if not os.path.exists(file_path):
        return 0
    elif not os.path.exists(os.path.join(file_path, 'game.exe')):
        return 1
    else:
        return 2
def find_scp_cbm(): # Find the path of SCP:CB Multiplayer
    value_name = 'SCP:CB_Multiplayer_Path'

    path_is_valid = False
    scp_path = None

    file_scp_path = read_setting_value(value_name)
    if file_scp_path is not None:
        valid_folder = check_if_scp_path_is_valid(file_scp_path)
        if valid_folder == 2:
            return file_scp_path
    try:
        # If the file doesn't exist, attempt to find the path
        possible_paths = [
            os.path.join(os.environ['PROGRAMFILES(X86)'], 'Steam'),
            os.path.join(os.environ['PROGRAMFILES'], 'Steam'),
        ]

        libraries = []
        
        # Gets each library registered in 'libraryfolders.vdf'
        for path in possible_paths:
            libraryfolders_path = os.path.join(path, 'steamapps', 'libraryfolders.vdf')
            if os.path.exists(libraryfolders_path):
                with open(libraryfolders_path, 'r') as f:
                    data = vdf.load(f)
                    libraries.extend(data['libraryfolders'].values())

        # Gets the path out of each library and checks if it contains SCP:CB Multiplayer
        for library in libraries:
            library_path = library['path']
            if library_path:
                scp_path = os.path.join(library_path, 'steamapps', 'common', 'SCP Containment Breach Multiplayer')
                if os.path.exists(scp_path):
                    path_is_valid = True
                    break
    finally:
        user_scp_path = None
        if not scp_path or not os.path.exists(scp_path):
            messages = {
                0: '''File path does not exist.
                ''',
                1: '''File path is not the game.
                '''
            }
            print("(reply with 'n' if the game is not installed)")
            while not path_is_valid:
                if user_scp_path:
                    valid_folder = check_if_scp_path_is_valid(user_scp_path)
                    if valid_folder in messages:
                        print('    ' + messages[valid_folder])
                    else:
                        path_is_valid = True
                        break
                user_scp_path = input('Please enter the path of SCP:CB Multiplayer: ')
                if user_scp_path.lower() != 'n':
                    scp_path = os.path.abspath(user_scp_path)
                else:
                    break

        if path_is_valid:
            change_setting(value_name, scp_path)
        else:
            print('It is reccomended to have the game installed whilst using gsIndexer.')

        return scp_path if path_is_valid else None