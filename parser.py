from typing import Any, Optional
from utils import Hub, Connection
import sys

class MapParser:
    def __init__(self, name_file: str):
        self.name_file = name_file
        self.nb_drones: int = 0
        self.hubs: dict[str, Hub] = {}
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
                    if cleaned_line and cleaned_line.find(":") == -1:
                        raise ValueError
        except OSError:
            print("[Error] There are issues with the settings file.")
            sys.exit(1)
        except ValueError:
            print("[Error] The format is key:value [optional=detail]")
            sys.exit(1)
        try:
            if settings[0].startswith("nb_drones:"):
                drones = int(settings[0].split(":")[1].strip())
                if drones < 0:
                    raise ValueError
                self.nb_drones = drones
  
        except ValueError:
            print("[Error] The settings file must begin with "
                  "nb_drones: (integer).")
            sys.exit(1)

        if not settings:
            print("[Error] The settings file must contain datas.")
            sys.exit(1)
        return settings

    def fetch_hub_datas(self):
        datas = self.fetch_infos()
        for data in datas:
            i = 0
            prefix, details = data.split(":")
            metadata = self.fetch_metadata(details)
            if "hub" in prefix:
                content: list = details.split()
                for meta in content:
                    if metadata and meta == metadata:
                        content.pop(i)
                    i += 1
                # metadata = [meta for meta in content if "[" in meta]
                # metadata += [meta for meta in content if "]" in meta]
                print(prefix)
                print(content)
                print(f"THAT'S META_DATA {metadata}")

        # return keys_values
    
    # def fetch_hub_datas(self):
    #     raw_hubs = self.fetch_infos()

    #     # datas = self.split_keys_values()
    #     # for data in datas:
    #     #     if data == "nb_drones":
    #     #         drones = datas[data]
    #     #         self.nb_drones = int(drones)
    #     #     elif data == "start_hub":
    #     #         name = datas[data].endswith(" ")
                

    def fetch_metadata(self, details: list):
        meta_data: str | None = ""
        if "[" and "]" in details:
            meta_data_start = details.index('[')
            meta_data_end = details.index(']')
            while meta_data_start < meta_data_end + 1:
                meta_data += details[meta_data_start]
                meta_data_start += 1
        if len(meta_data) <= 1:
            meta_data = None
        return meta_data
        
            


def main() -> None:
    settings = MapParser('config.txt')
    settings.fetch_hub_datas()
    # print(f"Key {test} ==> {test}")
    # print(settings.nb_drones)
    # settings.fetch_hub_datas()


if __name__ == "__main__":
    main()
