import json
from settings_manager import read_setting_value

json_file = '''
{
    "en": {
        "y": "y",
        "n": "n",
        "game must be installed": "WARNING: SCP:CBM must be installed.",
        "error": "ERROR",
        "successfully compiled": "Successfully Compiled!",
        "compile into gsc": "Compile into .gsc (y/n)?",
        "folder does not exist": "WARNING: The folder _ does not exist in the game's repository.",
        "no data written": "WARNING: No data was written to the file.",
        "indexing complete": "Indexing Complete!",
        "invalid choice enter": "Invalid choice. Please enter",
        "invalid choice": "   Invalid choice. Please enter",
        "path does not exist": "File path does not exist.",
        "path is not the game": "File path is not the game.",
        "no folders in workshopcontent": "    No mod folders detected inside of 'WorkshopContent'.",
        "please choose an option": "Please choose an option:",
        "automatic option": "1. Automatic mod folder path detection",
        "manual option": "2. Enter folder path manually",
        "kb": "KB",
        "please confirm this action": "Please confirm this action.",
        "mod folder": "Mod folder:",
        "quantity of files": "Quantity of files:",
        "gs size": "Approximated .gs size:",
        "proceed": "Proceed (y/n)?",
        "index another gs": "Index another .gs (y/n)?",
        "enter number choice": "Enter your choice (1/2):",
        "please choose a folder": "Please choose a folder",
        "enter x or y": "Enter (1, 2, 3...) or the name of the folder:",
        "enter folder path": "Enter your mod folder path:",
        "enter scp path": "Please enter the path of SCP:CB Multiplayer: ",
        "it is recommended to have the game installed": "It is recommended to have the game installed whilst using gsIndexer.",
        "reply if not installed": "(reply with 'n' if the game is not installed)"
    },
    "ru": {
        "y": "да",
        "n": "нет",
        "game must be installed": "ВНИМАНИЕ: SCP:CBM должен быть установлен.",
        "error": "ОШИБКА",
        "successfully compiled": "Успешно скомпилировано!",
        "compile into gsc": "Скомпилировать в .gsc (да/нет)?",
        "folder does not exist": "ВНИМАНИЕ: Папка _ не существует в хранилище игры.",
        "no data written": "ВНИМАНИЕ: B файл не было записано никаких данных.",
        "indexing complete": "Индексирование завершено!",
        "invalid choice enter": "Недействительный выбор. Пожалуйста, введите",
        "invalid choice": "   Недействительный выбор.",
        "path does not exist": "Путь к файлу не существует.",
        "path is not the game": "Путь к файлу - это не игра.",
        "no folders in workshopcontent": "    B папке 'WorkshopContent' не найдено ни одного аддона",
        "please choose an option": "Пожалуйста, выберите вариант:",
        "automatic option": "1. Автоматическое определение пути к папке c аддонами",
        "manual option": "2. Введите путь к папке вручную",
        "kb": "КБ",
        "please confirm this action": "Пожалуйста, подтвердите это действие.",
        "mod folder": "Название папки аддона:",
        "quantity of files": "Количество файлов:",
        "gs size": "Примерный размер файла .gs:",
        "proceed": "Приступать (да/нет)?",
        "index another gs": "Индексировать еще один .gs (да/нет)?",
        "enter number choice": "Введите свой выбор (1/2):",
        "please choose a folder": "Выберите папку",
        "enter x or y": "Введите (1, 2, 3...) или имя папки:",
        "enter folder path": "Укажите путь к папке c аддоном:",
        "enter scp path": "Пожалуйста, введите путь к SCP:CB Multiplayer: ",
        "it is recommended to have the game installed": "При использовании gsIndexer рекомендуется установить игру.",
        "reply if not installed": "(ответьте 'нет', если игра не установлена)"
    }
}
'''

translations = json.loads(json_file)

# Get the current language
current_language = read_setting_value("Translate_Into_Russian", False) and "ru" or "en"

# Function to get translated text
def translate(key: str) -> str:
    return translations.get(current_language, {}).get(key, key)