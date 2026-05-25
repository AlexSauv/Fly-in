from typing import Any, Optional
from utils import Hub, Connection
import sys

class MapParser:
    def __init__(self, name_file: str):
        self.name_file = name_file
        self.nb_drones: int = 0
        self.hubs: dict[str, Hub] = []
        self.connections: list[Connection] = []
        self.start_hub: Optional[Hub] = None
        self.end_hub: Optional[Hub] = None

    def fetch_infos(self) -> list[list[str]]:
        try:
            settings: list[str] = []
            with open(self.name_file, 'r') as file:
                for line in file:
                    cleaned_line = line.strip()
                    if cleaned_line and not cleaned_line.startswith("#"):
                        settings.append(cleaned_line)
        except OSError:
            print("[Error] There are issues with the settings file.")
            sys.exit(1)

        if not settings[0].startswith("nb_drones:"):
            print("[Error] The settings file must begin with "
                  "nb_drones: (integer).")
            sys.exit(1)
        if not settings:
            print("[Error] The settings file must contain datas.")
            sys.exit(1)
        return settings

    def split_keys_values(self):
        datas = self.fetch_infos()
        keys_values: dict = {}
        for data in datas:
            separator = data.find(":")
            if separator != -1 and data.count(':', 1):
                key, value = data.split(":")
                if key in keys_values:
                    keys_values[key].update({value.strip()})
                else:
                    keys_values.setdefault(key, {value.strip()})
            else:
                print("[Error] There are issues with the settings file.")
                print("[Error] The format is key:value [optional=detail]")
                sys.exit(1)
        return keys_values

    def fetch_metadata(self):
        settings = self.fetch_infos()
        for key in settings:
            optional = settings[key].strip('[]')
            options = []
            special = []
            if optional:
                options.append(optional.split(" "))
                for _ in options:
                    special.append(options.split("="))
                    if special > 1:
                        settings[key].setdefault("option",
                                                 {special[0]: special[1]})

            


def main() -> None:
    settings = MapParser('config.txt')
    test = settings.split_keys_values()
    print(f"Key {test} ==> {test.keys()}")


if __name__ == "__main__":
    main()
