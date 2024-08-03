import os
import subprocess
import settings_manager
from game_finder import find_scp_cbm
from translation_handler import translate as t
from termcolor import colored
os.system('color')

# Global Variables
file_info_cap: int = settings_manager.read_setting_value('File_Info_Cap', 10000)
file_auto_compile: bool = settings_manager.read_setting_value('Auto_Compile_Into_gsc', False)
file_show_info: bool = settings_manager.read_setting_value('Show_File_Info', True)
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

def compile_into_gsc(gs_file: str) -> None: # Run compiler.exe to compile .gs into .gsc
    if not scp_path:
        print(colored(f"\n    {t('game must be installed')}", 'yellow'))
        return None
    
    compiler = os.path.join(scp_path, 'SteamWorkshopUploader/ScriptsCompiler/compiler.exe')

    with open('compilersettings.ini', 'w') as file:
        file.write(f'compile {gs_file}\nexit')

    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    # Run compiler.exe
    with subprocess.Popen([compiler], startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
        output, error = process.communicate()

    # Check for errors
    if process.returncode != 0:
        print(colored(f"\n    {t('error')}: {error.decode()}", 'red'))
    else:
        print(f"\n    {t('successfully compiled')}")

    os.remove('compilersettings.ini')

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
                            game_path_string = f"'SCP:CBM/{folder}'"
                            warning_message = f"\n    {t('folder does not exist').replace('_', game_path_string)}"
                            print(colored(warning_message, 'yellow'))
                    output_lines.append(f'RedirectFile("{relative_path}", getscriptpath()+"\{relative_path}")')

        if len(output_lines) == 1:
            print(colored(f"\n    {t('no data written')}", 'yellow'))
        else:
            # Writes all of the found files to a .gs file
            with open(output_file_path, 'w') as f:
                f.write('\n'.join(output_lines))
            print(f"\n    {t('indexing complete')}")

            if file_auto_compile or get_choice(f"\n    {t('compile into gsc')} ", [t('y'), t('n')]) == t('y'):
                compile_into_gsc(output_file_path)
    except Exception as e:
        print(colored(f"\n    {t('error')}: {str(e)}\n", 'red'))

def get_file_info(start_path: str):
    # Get indexing information
    file_info = [0, 14]
    cap_num = False
    cap_size = False

    size_cap = file_info_cap * 1024
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
                    if file_info[0] < file_info_cap:
                        file_info[0] += 1
                    else:
                        file_info[0] = f'{file_info_cap - 1}+'
                        cap_num = True

                # Check if the value is not over the file cap
                if not cap_size:
                    file_path = os.path.join(dirpath, filename)
                    relative_path = os.path.relpath(file_path, start_path)
                    file_size = (len(relative_path) * 2 + 38)

                    if file_info[1] + file_size < size_cap:
                        file_info[1] += file_size
                    else:
                        file_info[1] = f'{file_info_cap - 1}+'
                        cap_size = True

    if not cap_size:
        file_info[1] = round(file_info[1] / 1024, 2)

    return file_info

def get_choice(prompt: str, options) -> str:
    while True:
        choice = input(prompt).lower()
        if choice in options:
            return choice
        print(f"    {t('invalid choice enter')} ({'/'.join(options)}).")

def get_existing_path(prompt: str) -> str:
    while True:
        path = os.path.abspath(input(prompt))
        if os.path.exists(path):
            return path
        print(f"    {t('path does not exist')}")

def get_mod_folder() -> str:
    if not scp_path:
        print(colored(t('game must be installed'), 'yellow'))
        return None
    mod_folder = os.path.join(scp_path, 'SteamWorkshopUploader', 'WorkshopContent')
    folders = [name for name in os.listdir(mod_folder) if os.path.isdir(os.path.join(mod_folder, name))]
    if not folders:
        print(t('no folders in workshopcontent'))
        return None
    prompt = f"\n{t('please choose a folder')}\n    {tuple(folders)}\n{t('enter x or y')} "
    while True:
        choice = input(prompt)
        folder = choice if not choice.isdigit() else folders[max(1, min(int(choice), len(folders))) - 1]
        folder_path = os.path.join(mod_folder, folder)
        if os.path.exists(folder_path):
            return folder_path
        print(t('invalid choice'))

def receive_idexing_directions() -> None:
    parent_path = settings_manager.get_parent_path()

    print(f"\n    {t('please choose an option')}\n\n    {t('automatic option')}\n    {t('manual option')}")
    choice = get_choice(f"\n{t('enter number choice')} ", ['1', '2'])
    folder_path = get_mod_folder() if choice == '1' else get_existing_path(f"\n{t('enter folder path')} ")
    if not folder_path:
        return receive_idexing_directions()

    if file_show_info:   
        file_info = get_file_info(folder_path)
        print(f""" 
        {t('please confirm this action')}
            
        {t('mod folder')} {os.path.basename(folder_path)}
        {t('quantity of files')} {file_info[0]}
        {t('gs size')} {file_info[1]} {t('kb')}""")
        
        if get_choice(f"\n{t('proceed')} ", [t('y'), t('n')]) == t('y'):
            write_gs_file(folder_path, parent_path)
    else:
        write_gs_file(folder_path, parent_path)

    if get_choice(f"\n{t('index another gs')} ", [t('y'), t('n')]) == t('y'):
        return receive_idexing_directions()

# Usage
receive_idexing_directions()