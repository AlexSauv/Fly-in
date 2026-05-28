from typing import Any, Optional
from utils import Hub, Connection, Zone_Type, Color
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
                    if metadata and meta in metadata:
                        content.pop(i)
                    i += 1
                print(prefix)
                print(content)
                print(f"THAT'S META_DATA {metadata}")
                if metadata:
                    options = self.get_metadata_attributes(metadata)
                self.generate_hub(prefix, content[0], content[1], content[2], options)
            if "connection" in prefix:
                content: list = details.split()
                names = content[0].split("-")
                print(names)
                if metadata:
                    options = self.get_metadata_attributes(metadata)
                self.generate_connections(names[0], names[1])
                
                
        print(self.connections)
        print(f"start_hub => {self.start_hub}")
        print(f"end hub => {self.end_hub}")


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
    settings.fetch_hub_datas()
    # print(f"Key {test} ==> {test}")
    # print(settings.nb_drones)
    # settings.fetch_hub_datas()


if __name__ == "__main__":
    main()
