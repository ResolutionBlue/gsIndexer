import os
from game_finder import find_scp_cbm, get_parent_path # type: ignore
from termcolor import colored
os.system('color')

# Constants
FILE_CAP: int = 10000

# Global Variables
scp_path: str = find_scp_cbm()

def get_nonexisting_folders(path: str, scp_path: str) -> str:
    # Find nonexistenting folders in the mod to print warnings
    if not scp_path:
        return None

    folders = path.split(os.sep)
    for i in range(2, len(folders) + 2):
        sub_path = os.sep.join(folders[:i])
        joined_path = os.path.join(scp_path, os.path.dirname(sub_path))
        if not os.path.exists(joined_path):
            return os.path.relpath(joined_path, scp_path)

    return None

def write_gs_file(folder_path: str, parent_path: str) -> None:
    try:
        folder_name = str(os.path.basename(folder_path)).replace(' ', '')
        output_file_path = os.path.join(parent_path, f'{folder_name}.gs')
        invalid_folders = set()
        output_lines = ['#playerscript']

        # Locate every file inside of the mod path
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                if not filename.endswith(('.gsc', '.gs')):
                    file_path = os.path.join(dirpath, filename)
                    relative_path = os.path.relpath(file_path, folder_path)
                    if scp_path and not any(folder in relative_path for folder in invalid_folders):
                        folder = get_nonexisting_folders(relative_path, scp_path)
                        if folder:
                            invalid_folders.add(folder)
                            print(colored(f"\n    WARNING: The folder 'GAME\{folder}' does not exist in the game's repository.", 'yellow'))
                    output_lines.append(f'RedirectFile("{relative_path}", getscriptpath()+"\{relative_path}")')

        if len(output_lines) == 1:
            print(colored('\n    WARNING: No data was written to the file.', 'yellow'))
        else:
            # Writes all of the found files to a .gs file
            with open(output_file_path, 'w') as f:
                f.write('\n'.join(output_lines))
            print('\n    Indexing Complete!')

    except Exception as e:
        print(colored(f'\n    ERROR: {str(e)}\n', 'red'))

def get_file_info(start_path: str):
    # Get indexing information
    file_info = [0, 14]
    cap_num = False
    cap_size = False

    size_cap = FILE_CAP * 1024
    for dirpath, dirnames, filenames in os.walk(start_path):
        if cap_num and cap_size:
            break

        for filename in filenames:
            if cap_num and cap_size:
                break

            # Make sure that the file is not one of the mod's used assets
            if not filename.endswith(('.gsc', '.gs')):
                # Check if the value is not over the file cap
                if not cap_num:
                    if file_info[0] < FILE_CAP:
                        file_info[0] += 1
                    else:
                        file_info[0] = f'{FILE_CAP - 1}+'
                        cap_num = True

                # Check if the value is not over the file cap
                if not cap_size:
                    file_path = os.path.join(dirpath, filename)
                    relative_path = os.path.relpath(file_path, start_path)
                    file_size = (len(relative_path) * 2 + 38)

                    if file_info[1] + file_size < size_cap:
                        file_info[1] += file_size
                    else:
                        file_info[1] = f'{FILE_CAP - 1}+'
                        cap_size = True

    if not cap_size:
        file_info[1] = round(file_info[1] / 1024, 2)

    return file_info

def get_choice(prompt: str, options) -> str:
    while True:
        choice = input(prompt).lower()
        if choice in options:
            return choice
        print(f'    Invalid choice. Please enter one of {options}.')

def get_existing_path(prompt: str) -> str:
    while True:
        path = os.path.abspath(input(prompt))
        if os.path.exists(path):
            return path
        print('    File path does not exist.')

def get_mod_folder() -> str:
    mod_folder = os.path.join(scp_path, 'SteamWorkshopUploader', 'WorkshopContent')
    folders = [name for name in os.listdir(mod_folder) if os.path.isdir(os.path.join(mod_folder, name))]
    if not folders:
        print('    No mod folders detected inside of "WorkshopContent".')
        return None
    prompt = f'\nPlease choose a folder\n    {folders}\nEnter (1, 2, 3...) or the name of the folder: '
    while True:
        choice = input(prompt)
        folder = choice if not choice.isdigit() else folders[max(1, min(int(choice), len(folders))) - 1]
        folder_path = os.path.join(mod_folder, folder)
        if os.path.exists(folder_path):
            return folder_path
        print('    Invalid choice.')

def receive_idexing_directions() -> None:
    parent_path = get_parent_path()

    print('\n    Please choose an option:\n\n    1. Automatic mod folder path detection\n    2. Enter folder path manually')
    choice = get_choice('\nEnter your choice (1 or 2): ', ['1', '2'])
    folder_path = get_mod_folder() if choice == '1' else get_existing_path('\nEnter your mod folder path: ')

    file_info = get_file_info(folder_path)
    print(f''' 
    Please confirm this action.
          
    Mod folder: {os.path.basename(folder_path)}
    Quantity of files: {file_info[0]}
    Approximated .gs size: {file_info[1]} KB''')
    
    if get_choice('\nProceed (y/n)? ', ['y', 'n']) == 'y':
        write_gs_file(folder_path, parent_path)

    if get_choice('\nIndex another .gs (y/n)? ', ['y', 'n']) == 'y':
        return receive_idexing_directions()


# Usage
receive_idexing_directions()