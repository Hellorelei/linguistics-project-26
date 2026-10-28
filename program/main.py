import io
import pathlib
import regex as re
import time

import requests
import json

from pathlib import Path


### CONFIG
API_DELAY = 1.0 # How long do we wait between each query? Allows us to respect API limits.
DEBUG_INFO = True
FILETYPE = "*.txt"
REGEX_PATTERN = re.compile(r"\p{L}+") # The pattern does not yet take into account changes with ' before vowels.

### Effects for the terminal
ENDC = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
FAIL = "\033[91m"
WARNING = "\033[93m"
SUCCESS = "\033[92m"
UP = "\033[1A"

### Formatting presets
BULLET = "·"
INDENT = "  "
STEP = "████▌"
CHECKMARK = f"{SUCCESS}{BOLD}✓{ENDC}"
ERR_SIGN = f"{FAIL}{BOLD}✕{ENDC}"
WARN_SIGN = f"{WARNING}{BOLD}▲{ENDC}"


class Tools:
    USR_INPUT_PREFIX = f"{DIM}>{ENDC}"

    @staticmethod
    def list_files(directory = Path.cwd(), file_suffix = FILETYPE) -> list:
        """List files of given type in directory."""
        files_in_dir = []
        globbed_files_in_dir = directory.glob(pattern = file_suffix)
        for file in globbed_files_in_dir:
            files_in_dir.append(file)
        return files_in_dir

    @staticmethod
    def select_directory() -> pathlib.Path:
        """Prompts user for a directory."""
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
        """Prompts user to continue or stop."""
        prompt_text = f"Continue? [{BOLD}Y{ENDC}/{BOLD}N{ENDC}] \n{Tools.USR_INPUT_PREFIX}"
        if input(prompt_text).strip().lower() == "y":
            return True
        else:
            return False


    @staticmethod
    def analyse_file(file:io.TextIOWrapper, filename="test.txt") -> dict:
        """Takes in an opened file and returns a dictionary containing:
        · nb_lines : int
        · nb_words : int
        · nb_unique_words : int
        · unique_words {
            "word" : "word"
        }
        """
        file_read = file.read()
        file_data = {
            "file_name": filename,
            "file_text": file_read,
            "nb_lines": 0,
            "nb_words": 0,
            "nb_unique_words": 0,
            "unique_words": {},
        }
        if DEBUG_INFO:
            print(f"==== analyse_file: file_data: \n{file_data}")

        for line in file_read.splitlines():
            file_data["nb_lines"] += 1
            for word in re.findall(REGEX_PATTERN, line):
                file_data["nb_words"] += 1
                if word in file_data["unique_words"]:
                    pass
                elif word not in file_data["unique_words"]:
                    file_data["unique_words"][word] = [word]
                    file_data["nb_unique_words"] += 1

        return file_data


    @staticmethod
    def insert_data_in_text(file_data: dict) -> str:
        """Uses file_data to tag adequate words in the provided text."""
        base_text:str = file_data["file_text"]
        temp_text = []

        # This lambda replaces words present in the database while avoiding duplicates.
        replace = lambda w: f"<w tag=\"{file_data["unique_words"][w.group()][2]}\" base=\"{file_data["unique_words"][w.group()][1]}\">{w.group()}</w>"

        for line in base_text.splitlines():
            if DEBUG_INFO:
                print(f"==== insert_data_in_text: line: {line}")
            updated_line = re.sub(REGEX_PATTERN, replace, line)
            if DEBUG_INFO:
                print(f"==== insert_data_in_text: updated_line: {updated_line}")
            temp_text.append(updated_line)

        if DEBUG_INFO:
            print(f"==== insert_data_in_text: temp_text: {temp_text}")
        updated_text = "\n".join(temp_text)
        if DEBUG_INFO:
            print(f"==== insert_data_in_text: updated_text: {updated_text}")
        return updated_text


    @staticmethod
    def get_info_for_word(word):
        """Return a list containing [word, lemma, tags] for the provided word.
        Checks if word is present in cache; if yes, return that; if not, fetch it from API."""
        lemma = ""
        tags = ""
        if word in DataCache.word_cache:
            lemma, tags = DataCache.word_cache[word]
        else:
            word_data = Tools.api_request_corpas_ie(word)
            if DEBUG_INFO:
                print(f"==== get_info_for_word word_data: {word_data}")
            lemma = word_data["lemma"]
            tags = word_data["tags"]
            DataCache.word_cache[word] = [lemma, tags]
        return [word, lemma, tags]


    @staticmethod
    def api_request_corpas_ie(word) -> dict:
        """Requests data from corpas.ie for the given word; returns [word, lemma, tags]"""
        r = requests.get(
            f"https://www.corpas.ie/noskeproxy.json?command=view&corpname=cng&viewmode=sen&q[]=q[lc=\"{word}\"]"
            + " within <doc/>&pagesize=1&fromp=1&attrs=word,tag,lemma"
        )
        #print(r)
        #print(r.text)
        #print("\n" * 4)
        #print(json.dumps(r.json(), indent=4))

        r_json = json.loads(r.text)
        relevant_data = r_json["Lines"][0]["Kwic"][1]
        if DEBUG_INFO:
            print(relevant_data)
        split_data = relevant_data["str"].split("/")
        if DEBUG_INFO:
            print(split_data)
        word_data = {
            "word": word,
            "lemma": split_data[2],
            "tags": split_data[1],
        }
        if DEBUG_INFO:
            print(f"==== api_request returned word_data: {word_data}")
        time.sleep(1)
        return word_data
# https://api.sketchengine.eu/bonito/run.cgi/view?corpname=preloaded/bnc2&json={"corpname":"preloaded/bnc2", "q":["q[lemma=\"test\"]", "r250"]}
# https://api.sketchengine.eu/bonito/run.cgi/wordlist?corpname=preloaded/bnc2&wlattr=word&keywords=1&usesubcorp=wri-to-be-spoken&wlsort=frq&wlmaxitems=2&ref_corpname=preloaded/bnc&format=json
# https://www.corpas.ie/en/cng/?q=bhean%20ba%20léanmhar
# https://api.sketchengine.eu/bonito/run.cgi/wsketch?corpname=XXX&lemma=test&lpos=-n
# https://www.corpas.ie/noskeproxy.json?command=view&corpname=cng&viewmode=sen&q%5B%5D=q%5Blc%3D%22bhean%22%7Clemma_lc%3D%22bhean%22%5D%20within%20%3Cdoc%2F%3E&q%5B%5D=e200&kwicleftctx=-25&kwicrightctx=25&pagesize=40&fromp=1&attrs=word%2Clemma%2Ctag&ctxattrs=word%2Clemma%2Ctag&structs=g&refs=doc.file%2Cdoc.year%2Cdoc.medium%2Cdoc.textType%2Cdoc.genre%2Cdoc.topic%2Cdoc.author%2Cdoc.title%2Cdoc.url%2Cdoc.source%2Cdoc.publisher
# https://www.corpas.ie/noskeproxy.json?command=view&corpname=cng&viewmode=sen&q%5B%5D=q%5Blc%3D%22bhean%22%7Clemma_lc%3D%22bhean%22%5D%20%5B%5D%7B0%2C2%7D%20%5Blc%3D%22ba%22%7Clemma_lc%3D%22ba%22%5D%20%5B%5D%7B0%2C2%7D%20%5Blc%3D%22léanmhar%22%7Clemma_lc%3D%22léanmhar%22%5D%20within%20%3Cdoc%2F%3E&q%5B%5D=e200&kwicleftctx=-25&kwicrightctx=25&pagesize=40&fromp=1&attrs=word%2Clemma%2Ctag&ctxattrs=word%2Clemma%2Ctag&structs=g&refs=doc.file%2Cdoc.year%2Cdoc.medium%2Cdoc.textType%2Cdoc.genre%2Cdoc.topic%2Cdoc.author%2Cdoc.title%2Cdoc.url%2Cdoc.source%2Cdoc.publisher


class DataCache:
    """Holds cached data and caches new data."""
    word_cache = {}

    @staticmethod
    def reset_cache():
        """Empties word cache."""
        word_cache = {}
        print(f"{CHECKMARK} Cache reset.{ENDC}")

    @staticmethod
    def cache_word(word: str, lemma: str, tags: str):
        """Create an entry for word containing [lemma, tags]."""
        if word not in DataCache.word_cache:
            DataCache.word_cache[word] = [lemma, tags]


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
        ProgramLoop.step_set_input()


    @staticmethod
    def step_set_input():
        """Prompts user for input directory."""
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
        ProgramLoop.step_set_output()


    @staticmethod
    def step_set_output():
        """Prompts user for output directory."""
        print(f"{BOLD}{STEP}2. Selecting output{ENDC}")
        while True:
            output_directory = Tools.select_directory()
            files_in_dir = Tools.list_files(output_directory)
            if len(files_in_dir) > 0:
                print(f"{WARN_SIGN}{WARNING} Warning: output directory already contains files.{ENDC}")
                break
            elif len(files_in_dir) == 0:
                print(f"{CHECKMARK} Directory is empty.{ENDC}")
                break
            else:
                pass

        while True:
            if Tools.continue_prompt():
                ProgramLoop.selected_output_dir = output_directory
                break
        ProgramLoop.step_process_loop()


    @staticmethod
    def step_process_loop():
        print(f"{BOLD}{STEP}3. Processing{ENDC}")
        for file in ProgramLoop.selected_input_dir.glob(pattern = FILETYPE):
            current_file = file.name
            print(f"{BULLET} File: {current_file}")
            print(f"{INDENT}{DIM}├analysing file..{ENDC}")

            with open(file, "r", encoding="utf-8") as opened_file:
                #file_text = opened_file.read()
                #print(file_text)
                file_data = Tools.analyse_file(opened_file, current_file)
                nb_lines = file_data["nb_lines"]
                nb_words = file_data["nb_words"]
                nb_unique_words = file_data["nb_unique_words"]
                print(f"{INDENT}{DIM}├lines: {nb_lines:<4} words: {nb_words:<4} unique words: {nb_unique_words:<4}{ENDC}")

                for word in file_data["unique_words"]:
                    file_data["unique_words"][word] = Tools.get_info_for_word(word)

            tagged_text = Tools.insert_data_in_text(file_data)
            print(f"!!! final output: {tagged_text}")
            output_file = Path(ProgramLoop.selected_output_dir).joinpath(current_file).resolve()
            with open(output_file, "w", encoding="utf-8") as write_file:
                write_file.write(tagged_text)
            if DEBUG_INFO:
                print(file_data)


def main():
    while True:
        ProgramLoop.welcome()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
