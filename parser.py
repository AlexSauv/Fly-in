from typing import Any
import sys
from pydantic import Basemodel, ValidatorError

class MapParser:
    def __init__(self, name_file, keys_values: list[str]):
        self.name_file = name_file
        self.keys_values = keys_values

    def fetch_infos() -> list[list[str]]:
        try:
            file = sys.argv[1]
            settings: list[str] = []
            with open(file, 'r'):
                for line in file:
                    if not line.strip().startswith("#"):
                        settings.append(line.strip())
        except OSError:
            print("[Error] There are issues with the settings file.")
            sys.exit(1)
        keys_values = [list[str]]
        for line in settings:
            separator = line.find("=")
            if separator != -1 and line.count('=') == 1:
                keys_values.append(line.split("="))
            else:
                print("[Error] There are issues with the settings file.")
                sys.exit(1)
        return keys_values

def 