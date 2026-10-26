# This is a sample Python script.
import pathlib
# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

from pathlib import Path

### Effects for the terminal
ENDC = '\033[0m'
BOLD = '\033[1m'
DIM = '\033[2m'
FAIL = '\033[91m'
WARNING = '\033[93m'
SUCCESS = '\033[92m'

### Formatting presets
BULLET = '·'
INDENT = '  '
STEP = '▌'

### Global variables
input_directory = pathlib.Path()
output_directory = pathlib.Path()


class UserPrompts:
    USR_INPUT_PREFIX = f'{DIM}>{ENDC}'
    def __init__(self):
        pass

    @staticmethod
    def select_directory() -> pathlib.Path:
        selected_dir = pathlib.Path().cwd()
        prompt_text = f"Please enter a directory: \n{UserPrompts.USR_INPUT_PREFIX}"
        dir_error = f"{WARNING}Directory not found or not valid.{ENDC}"
        while True:
            selected_dir_str = input(prompt_text).replace('\'', '')
            selected_dir = Path(selected_dir_str)
            selected_dir = selected_dir.resolve()
            #print(f"selected dir: {selected_dir}")
            if selected_dir.is_dir():
                return selected_dir
            else:
                print(dir_error)


    @staticmethod
    def continue_prompt() -> bool:
        prompt_text = f"Continue? [Y/N]"
        if input(prompt_text).strip().lower() == 'y':
            return True
        else:
            return False






class ProgramInterface:
    selected_dir = pathlib.Path()

    def __init__(self):
        print("hi")


    @staticmethod
    def welcome():
        print(f"{DIM}This program was made in October 2026 by Lorelei C.{ENDC}\n")
        print(f"{DIM}┌{BOLD}Input{ENDC}{DIM}: a directory containing text files with a .txt suffix.{ENDC}")
        print(f"{DIM}├{BOLD}Process{ENDC}{DIM}: text files are processed as follows:{ENDC}")
        print(f"{DIM}│{INDENT}1. The user points the program at the text files.{ENDC}")
        print(f"{DIM}│{INDENT}2. For each file, the program loads the text, and uses REGEX to:{ENDC}")
        print(f"{DIM}│{INDENT*2} i. split it into lines;{ENDC}")
        print(f"{DIM}│{INDENT*2}ii. split it into words.{ENDC}")
        print(f"{DIM}│{INDENT}3. The program queries a database for information on each word.{ENDC}")
        print(f"{DIM}│{INDENT}4. The information is embedded into the text file.{ENDC}")
        print(f"{DIM}└{BOLD}Output{ENDC}{DIM}: the text files with embedded data are saved to a user-selected directory.{ENDC}")
        print(f"\n{DIM}To quit the program, press CTRL+C.{ENDC}")
        ProgramInterface.step_input()


    @staticmethod
    def step_input():
        global input_directory
        print(f"{BOLD}{STEP}1. Opening source{ENDC}")
        input_directory = UserPrompts.select_directory()
        files_in_dir = []
        globbed_files_in_dir = input_directory.glob('*.txt')
        for file in globbed_files_in_dir:
            files_in_dir.append(file)

        #print(files_in_dir)
        nb_files_in_dir = len(files_in_dir)
        print(f"{SUCCESS}{BOLD}✓{ENDC} Found {nb_files_in_dir} files.{ENDC}")


    @staticmethod
    def step_process():
        pass


def main():
    while True:
        ProgramInterface.welcome()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
