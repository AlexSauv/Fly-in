from typing import Any, Optional
from utils import Hub, Connection, Zone_Type, Color
import re
import sys

class MapParser:
    def __init__(self, name_file: str):
        self.name_file = name_file
        self.nb_drones: int = 0
        self.hubs: dict[str, Hub] = {}
        self.connections: list[Connection] = []
        self.start_hub: Optional[Hub] = None
        self.end_hub: Optional[Hub] = None

    def fetch_infos(self) -> list[str]:
        settings: list[str] = []
        try:
            with open(self.name_file, 'r') as file:
                for line_num, line in enumerate(file, 1):
                    cleaned_line = line.strip()
                    if not cleaned_line or cleaned_line.startswith("#"):
                        continue
                    if ":" not in cleaned_line:
                        print(f"[Error] Line {line_num} The format is 'key:value [optional=detail]'")
                        sys.exit(1)

                    settings.append(cleaned_line)
        except OSError:
            print(f"[Error] Cannot read file named: {self.name_file}.")
            sys.exit(1)
        if not settings:
            print("[Error] Empty datas setting.")
            sys.exit(1)
        return settings

    def get_main_settings(self) -> None:
        lines: list[str] = self.fetch_infos()
        if not lines[0].startswith("nb_drones:"):
            print("[Error] Setting file must begin with 'nb_drones:int'")
            sys.exit(1)
        try:
            self.nb_drones = int(lines[0].split(":")[1].strip())
            if self.nb_drones <= 0:
                raise ValueError
        except ValueError:
            print("[Error] 'nb_drones' must be a positive integer")
            sys.exit(1)

        for line in lines[1:]:
            prefix, details = line.split(":")
            prefix = prefix.strip()
            content, metadata = self.fetch_metadata(details)
            settings = content.split()
            
            if prefix in ("hub", "start_hub", "end_hub"):
                if len(settings) != 3:
                    print("[ERROR] Not the right number of arguments, "
                          " You need 'name' 'pos one' 'pos two'")
                    sys.exit(1)
                
            # print(f"PREFIX ===> {prefix}")
            # print(f"CONTENT ====> {details}")
            #     print(f"THAT'S META_DATA {metadata}")
            #     if metadata:
            #         options = self.get_metadata_attributes(metadata)
            #     self.generate_hub(prefix, content[0], content[1], content[2], options)
            # if "connection" in prefix:
            #     content: list = details.split()
            #     names = content[0].split("-")
            #     print(names)
            #     if metadata:
            #         options = self.get_metadata_attributes(metadata)
            #     self.generate_connections(names[0], names[1])
                
                
        # print(self.connections)
        # print(f"start_hub => {self.start_hub}")
        # print(f"end hub => {self.end_hub}")


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


    def fetch_metadata(self, details: str) -> tuple[str, dict[str, str]]:
        meta_data: dict[str, str] = {}
        match = re.search(r'\[(.*?)\]', details)

        if match:
            meta_content = match.group(1)
            main_settings = details.replace(match.group(0), '').strip()
            for part in meta_content.split():
                if "=" not in part:
                    print("Metadata must be '[details=infos]'")
                    sys.exit(1)
                key, value = part.split("=")
                meta_data[key] = value

        else:
            main_settings = details
            meta_content = None
        return main_settings, meta_data
    
    def get_metadata_attributes(self, metadata: str) -> None:
        try:
            meta = metadata.strip("[]")
            parts = meta.split()
            datas = {}
            for part in parts:
                if "=" not in part:
                    raise ValueError("Metadatas must be given as [optional=data optional=data]")
                else:
                    key, value = part.split("=")
                if key == "zone":
                    datas.setdefault(key, value)
                elif key == "color":
                    datas.setdefault(key, value)
                elif key == "max_drones":
                    datas.setdefault(key, value)
                elif key == "max_link_capacity":
                    datas.setdefault(key, value)
                else:
                    raise ValueError("Option unknown make sure to add"
                                     " the right options")
        except Exception as e:
            print(f"[Error] {e}")
            sys.exit(1)
        print(f"\n\n\n{datas.items()}\n\n\n")
        return datas

    def generate_hub(self, prefix: str,
                     name_hub: str, row: str, col: str, metadata: dict) -> None:
        try:
            pos: tuple = (int(row), int(col))
            zone = Zone_Type.NORMAL.value
            color_choose = None
            if "zone" in metadata:
                if metadata["zone"] == "normal":
                    zone = Zone_Type.NORMAL.value
                elif metadata["zone"] == "blocked":
                    zone = Zone_Type.BLOCKED.value
                elif metadata["zone"] == "restricted":
                    zone = Zone_Type.RESTRICTED.value
                elif metadata["zone"] == "priority":
                    zone = Zone_Type.PRIORITY.value
                else:
                    raise ValueError("Zone type unknown")
            # if "color" in metadata:
            #     if metadata["color"] not in Color:
            #         raise ValueError("Unknown color")
            #     color_choose = Color(metadata["color"])
            #     for color in Color:
            #         if metadata["color"] == color:
            #             hub_color = color_choose.value
            # # if metadata["color"] in metadata:
                
            hub = Hub(name=name_hub,
                      zone_type=zone,
                    #   color=hub_color,
                      position=pos
                      )
            if not hub:
                print("Cannot create the hub, not found enough datas.")
                sys.exit(1)
            self.hubs.setdefault(name_hub, hub)
            if prefix == "start_hub":
                self.start_hub = hub
            if prefix == "end_hub":
                self.end_hub = hub
            
        except Exception as e:
            print(f"[Error] {e}")
            sys.exit(1)
            
    def generate_connections(self, name_one: str, name_two: str) -> None:
        try:
            link = []
            for hub in self.hubs:
                if hub.name == name_one:
                    link.append(hub)
                if hub.name == name_two:
                    link.append(hub)
            if len(link) != 2:
                raise ValueError("The connection needs 2 hubs")
            
            connect = Connection(hub_name_a=name_one,
                                    hub_name_b=name_two,
                                    zones=link
                                    ) 
            self.connections.append(connect)
        except Exception as e:
            print(f"[Error] {e}")
        


def main() -> None:
    settings = MapParser('config.txt')
    settings.get_main_settings()
    # print(f"Key {test} ==> {test}")
    # print(settings.nb_drones)
    # settings.fetch_hub_datas()


if __name__ == "__main__":
    main()
