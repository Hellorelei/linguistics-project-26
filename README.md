# linguistics-project-26

This program is a proof-of-concept that aims to demonstrate how public resources such as the National Corpus of Irish foster linguistics research.

As it stands, the program is a part-of-speech tagger for Irish based on contextless requests to the National Corpus of Irish. It it likely that the tags will make sense, but **the data is not adequate for any further research of training**.

We hope that this program can instead inspire further development in the field of Irish linguistics.

## Installation

This program is written in Python. It may require the installation of the `regex` and `requests` modules. It is meant to be executed as a command-line program.

Testing has only been done on macOS.

 1. **Ensure that you have Python installed.** The program works with Python 3.14; previous versions have not been tested.
 2. **Create a virtual environment for the program**. On macOS, you can do so using the `python3.14 -m venv .venv` command in the working directory for the program.
 3. **Ensure that `regex` and `requests` are installed.** You can install them yourself in the virtual environment by activating it (see next step) and entering `python3.14 pip -m install <package_name>`.
 4. **Activate the virtual environment** by entering `source .venv/bin/activate` on macOS.
 5. **Start the program** by entering `python3.14 main.py`.
