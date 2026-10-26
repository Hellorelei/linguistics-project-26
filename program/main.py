import pathlib
import sys

import requests
import json

from pathlib import Path

### API
API_DELAY = 1.0 # How long do we wait between each query? Allows us to respect API limits.

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
STEP = '████▌'
CHECKMARK = f'{SUCCESS}{BOLD}✓{ENDC}'
ERR_SIGN = f'{FAIL}{BOLD}✕{ENDC}'


class Tools:
    USR_INPUT_PREFIX = f'{DIM}>{ENDC}'

    @staticmethod
    def list_files(directory = Path.cwd(), file_suffix = "*.txt") -> list:
        files_in_dir = []
        globbed_files_in_dir = directory.glob(pattern = file_suffix)
        for file in globbed_files_in_dir:
            files_in_dir.append(file)
        return files_in_dir

    @staticmethod
    def select_directory() -> pathlib.Path:
        selected_dir = pathlib.Path().cwd()
        prompt_text = f"Please enter a directory: \n{Tools.USR_INPUT_PREFIX}"
        dir_error = f"{ERR_SIGN} {FAIL}Directory not found or not valid.{ENDC}"
        while True:
            selected_dir_str = input(prompt_text).replace('\'', '')
            selected_dir = Path(selected_dir_str)
            selected_dir = selected_dir.resolve()
            print(f"{DIM}{BULLET} Computed directory: {selected_dir}{ENDC}")
            if selected_dir.is_dir():
                return selected_dir
            else:
                print(dir_error)


    @staticmethod
    def continue_prompt() -> bool:
        prompt_text = f"Continue? [{BOLD}Y{ENDC}/{BOLD}N{ENDC}] \n{Tools.USR_INPUT_PREFIX}"
        if input(prompt_text).strip().lower() == 'y':
            return True
        else:
            return False

    @staticmethod
    def get_info_for_word(word):
        lemma = ""
        tags = ""
        return [word, lemma, tags]


    @staticmethod
    def api_request_corpas_ie(word) -> dict:

        r = requests.get(
            f"https://www.corpas.ie/noskeproxy.json?command=view&corpname=cng&viewmode=sen&q[]=q[lc=\"{word}\"]"
            + " within <doc/>&pagesize=1&fromp=1&attrs=word,tag,lemma"
        )
        print(r)
        print(r.text)
        print("\n" * 4)
        print(json.dumps(r.json(), indent=4))

        r_json = json.loads(r.text)
        relevant_data = r_json["Lines"][0]["Kwic"][1]
        print(relevant_data)
        split_data = relevant_data["str"].split("/")
        print(split_data)
        word_data = {
            "word": word,
            "lemma": split_data[2],
            "tag": split_data[1],
        }
        print(word_data)

        return word_data
# https://api.sketchengine.eu/bonito/run.cgi/view?corpname=preloaded/bnc2&json={"corpname":"preloaded/bnc2", "q":["q[lemma=\"test\"]", "r250"]}
# https://api.sketchengine.eu/bonito/run.cgi/wordlist?corpname=preloaded/bnc2&wlattr=word&keywords=1&usesubcorp=wri-to-be-spoken&wlsort=frq&wlmaxitems=2&ref_corpname=preloaded/bnc&format=json
# https://www.corpas.ie/en/cng/?q=bhean%20ba%20léanmhar
# https://api.sketchengine.eu/bonito/run.cgi/wsketch?corpname=XXX&lemma=test&lpos=-n
# https://www.corpas.ie/noskeproxy.json?command=view&corpname=cng&viewmode=sen&q%5B%5D=q%5Blc%3D%22bhean%22%7Clemma_lc%3D%22bhean%22%5D%20within%20%3Cdoc%2F%3E&q%5B%5D=e200&kwicleftctx=-25&kwicrightctx=25&pagesize=40&fromp=1&attrs=word%2Clemma%2Ctag&ctxattrs=word%2Clemma%2Ctag&structs=g&refs=doc.file%2Cdoc.year%2Cdoc.medium%2Cdoc.textType%2Cdoc.genre%2Cdoc.topic%2Cdoc.author%2Cdoc.title%2Cdoc.url%2Cdoc.source%2Cdoc.publisher
# https://www.corpas.ie/noskeproxy.json?command=view&corpname=cng&viewmode=sen&q%5B%5D=q%5Blc%3D%22bhean%22%7Clemma_lc%3D%22bhean%22%5D%20%5B%5D%7B0%2C2%7D%20%5Blc%3D%22ba%22%7Clemma_lc%3D%22ba%22%5D%20%5B%5D%7B0%2C2%7D%20%5Blc%3D%22léanmhar%22%7Clemma_lc%3D%22léanmhar%22%5D%20within%20%3Cdoc%2F%3E&q%5B%5D=e200&kwicleftctx=-25&kwicrightctx=25&pagesize=40&fromp=1&attrs=word%2Clemma%2Ctag&ctxattrs=word%2Clemma%2Ctag&structs=g&refs=doc.file%2Cdoc.year%2Cdoc.medium%2Cdoc.textType%2Cdoc.genre%2Cdoc.topic%2Cdoc.author%2Cdoc.title%2Cdoc.url%2Cdoc.source%2Cdoc.publisher

class ProgramLoop:
    selected_input_dir = pathlib.Path().cwd()
    selected_output_dir = pathlib.Path().cwd()
    # We compare the amount of files in input vs in output to make sure nothing is missing.
    files_in_input_dir = 0
    files_in_output_dir = 0


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
        print(f"\n{DIM}To quit the program, press CTRL+C.{ENDC}\n")
        ProgramLoop.step_input()


    @staticmethod
    def step_input():
        print(f"{BOLD}{STEP}1. Selecting source{ENDC}")
        while True:
            input_directory = Tools.select_directory()
            print(input_directory)
            files_in_dir = Tools.list_files(input_directory)
            print(files_in_dir)
            if len(files_in_dir) > 0:
                print(f"{CHECKMARK} Found {len(files_in_dir)} files.{ENDC}")
                break
            else:
                print(f"{ERR_SIGN} {FAIL}No valid files in selected directory.{ENDC}")

        while True:
            if Tools.continue_prompt():
                ProgramLoop.selected_input_dir = input_directory
                ProgramLoop.files_in_input_dir = files_in_dir
                break
        ProgramLoop.step_output()


    @staticmethod
    def step_output():
        print(f"{BOLD}{STEP}2. Selecting output{ENDC}")
        while True:
            output_directory = Tools.select_directory()
            files_in_dir = Tools.list_files(output_directory)
            if len(files_in_dir) > 0:
                print(f"{ERR_SIGN}{FAIL} Warning: output directory already contains files.{ENDC}")
            elif len(files_in_dir) == 0:
                print(f"{CHECKMARK} Directory is empty.{ENDC}")
                break
            else:
                pass

        while True:
            if Tools.continue_prompt():
                ProgramLoop.selected_output_dir = output_directory
                break


    @staticmethod
    def step_process():
        print(f"{BOLD}{STEP}3. Processing{ENDC}")
        print(f"i")


def main():
    Tools.api_request_corpas_ie("chéile")
    return
    while True:
        ProgramLoop.welcome()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
