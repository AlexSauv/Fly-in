from typing import Optional
from utils import Hub, Connection, ZoneType, Color
import re
import sys


class MapParser:
    def __init__(self, name_file: str):
        self.name_file = name_file
        self.nb_drones: int = 0
        self.hubs: dict[str, Hub] = {}
        self.connections: dict[str, Connection] = {}
        self.start_hub: Optional[Hub] = None
        self.end_hub: Optional[Hub] = None
        self.connected_to: dict[str, list[str]] = {}

    def fetch_infos(self) -> list[str]:
        settings: list[str] = []
        try:
            with open(self.name_file, 'r') as file:
                for line_num, line in enumerate(file, 1):
                    cleaned_line = line.strip()
                    if not cleaned_line or cleaned_line.startswith("#"):
                        continue
                    if ":" not in cleaned_line:
                        print(f"[Error] Line {line_num} The format is "
                              "'key:value [optional=detail]'")
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
        try:
            lines: list[str] = self.fetch_infos()
            if not lines[0].startswith("nb_drones:"):
                print("[Error] Setting file must begin with 'nb_drones:int'")
                sys.exit(1)

            self.nb_drones = int(lines[0].split(":")[1].strip())
            if self.nb_drones <= 0:
                raise ValueError("[Error] 'nb_drones' must be a"
                                 " positive integer")

            for line in lines[1:]:
                prefix, details = line.split(":")
                prefix = prefix.strip()
                content, metadata = self.fetch_metadata(details)
                settings = content.split()

                if prefix in ("hub", "start_hub", "end_hub"):
                    if len(settings) != 3:
                        print(settings)
                        print("[ERROR] Not the right number of arguments, "
                              " You need 'name' 'pos one' 'pos two'")
                        sys.exit(1)
                    self.generate_hub(prefix, settings[0],
                                      settings[1], settings[2], metadata)
                    
                elif prefix in ("connection"):
                    if len(settings) != 1:
                        print("[ERROR][CONNECTION] Not the right number of"
                              " arguments, e.g: 'name_hub1-name_hub2'")
                        sys.exit(1)
                    self.generate_connection(settings[0], metadata)

        except Exception as e:
            print(f"[ERROR]{e}")

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
                if key not in ("zone", "color",
                               "max_drones", "max_link_capacity"):
                    raise ValueError(f"[METADATA] {key} "
                                     "is an unknown type of metadata")
                meta_data[key] = value
        else:
            main_settings = details
            meta_content = None
        return main_settings, meta_data

    def generate_hub(self, prefix: str,
                     name_hub: str, row: str,
                     col: str, metadata: dict[str, str]) -> None:
        if "-" in name_hub:
            print("[Error] Hub name must not contains '-'.")
            sys.exit(1)
        if name_hub in self.hubs:
            print(f"[Error] Hub called {name_hub} already register.")
            sys.exit(1)

        pos: tuple[int, int] = (int(row), int(col))
        zone_data = metadata.get("zone")
        if not zone_data:
            zone = ZoneType.NORMAL.value
        elif zone_data == "normal":
            zone = ZoneType.NORMAL.value
        elif zone_data == "blocked":
            zone = ZoneType.BLOCKED.value
        elif zone_data == "restricted":
            zone = ZoneType.RESTRICTED.value
        elif zone_data == "priority":
            zone = ZoneType.PRIORITY.value
        else:
            raise ValueError(f"{zone_data} Zone type unknown")

        color_data = metadata.get("color")
        if not color_data:
            color_hub = Color.RED.value
        if color_data == "red":
            color_hub = Color.RED.value
        elif color_data == "purple":
            color_hub = Color.PURPLE.value
        elif color_data == "yellow":
            color_hub = Color.YELLOW.value
        elif color_data == "orange":
            color_hub = Color.ORANGE.value
        elif color_data == "blue":
            color_hub = Color.BLUE.value
        elif color_data == "green":
            color_hub = Color.GREEN.value
        else:
            raise ValueError(f" Color: {color_data} unknown, make sure to "
                             "write on lowercase.")

        max_drones_hub = int(metadata.get("max_drones", 1))
        hub = Hub(
            name=name_hub,
            zone_type=zone,
            color=color_hub,
            position=pos,
            max_drones=max_drones_hub
        )
        setattr(hub, 'drones', self.nb_drones if prefix == "start_hub" else 0)
        self.hubs.setdefault(name_hub, hub)
        if prefix == "start_hub" and not self.start_hub:
            self.start_hub = hub
        elif prefix == "start_hub" and self.start_hub:
            raise ValueError("There is already a start hub register.")

        if prefix == "end_hub" and not self.end_hub:
            self.end_hub = hub
        elif prefix == "end_hub" and self.end_hub:
            raise ValueError("There is already an end hub register.")

    def generate_connection(self, settings: str,
                            metadata: dict[str, str]) -> None:
        try:
            if "-" not in settings:
                raise ValueError("[CONNECTION] Names must be separate by '-'")
            if settings in self.connections:
                raise ValueError("[CONNECTION] Connection already register.")
            names = settings.split("-")
            name_one = names[0].strip()
            name_two = names[1].strip()
            if len(names) != 2:
                raise ValueError("[CONNECTION] The connection needs 2 hubs")
            if name_one not in self.hubs:
                raise ValueError(f"[CONNECTION]{name_one}"
                                 " not found in our datas.")
            if name_two not in self.hubs:
                raise ValueError(f"[CONNECTION]{name_two}"
                                 " not found in our datas.")
            hub_a = self.hubs[name_one]
            hub_b = self.hubs[name_two]
            max_capacity = int(metadata.get("max_link_capacity", 1))
            connect = Connection(hub_name_a=name_one,
                                 hub_name_b=name_two,
                                 hubs=[hub_a, hub_b],
                                 max_link_capacity=max_capacity
                                 )
            self.connections.setdefault(settings, connect)
            self.connected_to.setdefault(name_one, []).append(name_two)
            self.connected_to.setdefault(name_two, []).append(name_one)
        except Exception as e:
            print(f"[ERROR]{e}")


# def main() -> None:
    
#     settings.get_main_settings()
#     # print(f"Key {test} ==> {test}")
#     # print(settings.nb_drones)
#     # settings.fetch_hub_datas()


# if __name__ == "__main__":
#     main()
