import os
import sys
import vdf
from termcolor import colored
os.system('color')

def get_script_path(): # Get the scripts file path
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.realpath(__file__))

def check_if_scp_path_is_valid(file_path):
    file_path = os.path.abspath(file_path)
    if not os.path.exists(file_path):
        return 0
    elif not os.path.exists(os.path.join(file_path, 'game.exe')):
        return 1
    else:
        return 2
def find_scp_cb_multiplayer(): # Find the path of SCP:CB Multiplayer
    value_name = 'SCP:CBMultiplayerPath='

    file_name = os.path.join(get_script_path(), 'settings.ini')
    path_is_valid = False
    scp_path = None

    # Check if the file exists
    if os.path.exists(file_name):
        # If the file exists, read the path from the file
        with open(file_name, 'r') as file:
            file_content = file.read()
            if file_content.startswith(value_name):
                file_scp_path = file_content.replace(value_name, '')
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
                        print("    " + messages[valid_folder])
                    else:
                        path_is_valid = True
                        break
                user_scp_path = input('Please enter the path of SCP:CB Multiplayer: ')
                if user_scp_path.lower() != 'n':
                    scp_path = os.path.abspath(user_scp_path)
                else:
                    user_scp_path = user_scp_path.lower()

        if path_is_valid:
            with open(file_name, 'w') as file:
                file.write(value_name + scp_path)
        else:
            print(colored(fr'It is reccomended to have the game installed whilst using gsIndexer.', 'black', 'on_white'))

        return scp_path if path_is_valid else None
scp_path = find_scp_cb_multiplayer()

def get_nonexistenting_folders(path, scp_path): # Find nonexistenting folders in the mod to print warnings
    if scp_path:
        folders = path.split(os.sep)
        for i in range(2, len(folders) + 2):
            sub_path = os.sep.join(folders[:i])
            joined_path = os.path.join(scp_path, os.path.dirname(sub_path))
            if not os.path.exists(joined_path):
                return os.path.relpath(joined_path, scp_path)
        return None

def get_file_info(start_path): # Get the script's path
    file_cap = 10000

    file_info = [0, 0]
    cap_num = False
    cap_size = False
    for dirpath, dirnames, filenames in os.walk(start_path):
        for filename in filenames:
            # Make sure that the file is not one of the mod's used assets
            if not filename.endswith(('.gsc', '.gs', '.exe')):
                # Check if the value is not over the file cap
                if not cap_num:
                    if file_info[0] < file_cap:
                        file_info[0] += 1
                    else:
                        file_info[0] = f'{file_cap - 1}+'
                        cap_num = True
                # Check if the value is not over the file cap
                if not cap_size:
                    if file_info[1] < file_cap:
                        file_path = os.path.join(dirpath, filename)
                        relative_path = os.path.relpath(file_path, start_path)
                        file_info[1] += (len(relative_path) * 2 + 38) / 1024
                    else:
                        file_info[1] = f'{file_cap - 1}+'
                        cap_size = True
        if cap_num and cap_size:
            break
    if not cap_size:
        file_info[1] = round(file_info[1], 2)
    return file_info

def write_gs_file(folder_path, script_path):
    try:
        folder_name = str(os.path.basename(folder_path)).replace(' ', '')
        output_file_path = os.path.join(script_path, f'{folder_name}.gs')
        invalid_folders = []
        # Locate every file inside of the mod path and write a line
        with open(output_file_path, 'w') as f:
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for filename in filenames:
                    # Make sure that the file is not one of the mod's used assets
                    if not filename.endswith(('.gsc', '.gs', '.exe')):
                        file_path = os.path.join(dirpath, filename)
                        relative_path = os.path.relpath(file_path, folder_path)
                        if scp_path and not any(folder in relative_path for folder in invalid_folders):
                            folder = get_nonexistenting_folders(relative_path, scp_path)
                            # If the "get_nonexistenting_folders" gives back a value, it prints a warning
                            if folder:
                                invalid_folders.append(folder)
                                print(colored(f'''
    WARNING: The folder "GAME\{folder}" does not exist in the game's repository.''', 'yellow'))
                        f.write(f'RedirectFile("{relative_path}", getscriptpath()+"\{relative_path}")\n')
        if os.stat(output_file_path).st_size == 0:
            print(colored('''
    WARNING: No data was written to the file.''', 'yellow'))
        print('''
    Indexing Complete!
              ''')
    except Exception as e:
        # If an error accurs, it prints out an error message
        print(colored(f'''
    ERROR: {str(e)}
               %s''', 'red'))

def receive_idexing_directions():
    script_path = get_script_path()

    print('''
    Please choose an option:

    1. Automatic mod folder path detection
    2. Enter folder path manually''')
    while True:
        # Set folder path depending on user input
        choice = input('''
Enter your choice (1 or 2): ''')
        if choice == '1': # Automatic option
            if scp_path:
                while True:
                    mod_folder = os.path.join(scp_path, 'SteamWorkshopUploader', 'WorkshopContent')
                    folders = [name for name in os.listdir(mod_folder) if os.path.isdir(os.path.join(mod_folder, name))]
                    if folders:
                        choice = input(f'''
Please choose a folder
    {folders}
Enter (1, 2, 3...) or the name of the folder: ''')
                        if choice.isdigit():
                            number = max(1, min(int(choice), len(folders)))
                            folder_path = os.path.join(mod_folder, folders[number - 1])
                        else:
                            folder_path = os.path.join(mod_folder, choice)
                        if os.path.exists(folder_path):
                            break
                        else:
                            print('    Invalid choice.')
                    else:
                        print('    No mod folders detected inside of "WorkshopContent".')
                break
            else:
                print('    SCP:CB Multiplayer must be installed.')
        elif choice == '2': # Manual option
            while True:
                path = input('''
Enter your mod folder path: ''')
                abs_path = os.path.abspath(path)
                if not os.path.exists(abs_path):
                    print('    File path does not exist.')
                else:
                    break
            folder_path = os.path.abspath(abs_path)
            break
        else:
            print('    Invalid choice. Please enter 1 or 2.')
    # Give the user information about the action
    file_info = get_file_info(folder_path)
    print(f'''
    Please confirm this action.

    Mod folder: {os.path.basename(folder_path)}
    Quantity of files: {file_info[0]}
    Approximated .gs size: {file_info[1]} KB
           ''')
    while True:
        choice = input('Proceed (y/n)? ')
        if choice.lower() == 'y':
            write_gs_file(folder_path, script_path) 
            break
        elif choice.lower() == 'n':
            break
        else:
            print('''   Invalid choice. Please enter y or n.
                  ''')
    while True:
        # Once finished, ask whether the user wants to restart or not
        choice = input('Index another .gs (y/n)? ')
        if choice.lower() == 'y':
            return receive_idexing_directions()
        elif choice.lower() == 'n':
            break
        else:
            print('''   Invalid choice. Please enter y or n.
                  ''')

# Usage
receive_idexing_directions()