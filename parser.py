from utils import Hub, Connection, ZoneType, Color, Drone
import re
import sys


class MapParser:
    def __init__(self, name_file: str):
        self.name_file = name_file
        self.nb_drones: int = 0
        self.hubs: dict[str, Hub] = {}
        self.connections: dict[str, Connection] = {}
        self.start_hub: Hub = None
        self.end_hub: Hub = None
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
                raise ValueError(" Setting file must"
                                 " begin with 'nb_drones:int'")

            self.nb_drones = int(lines[0].split(":")[1].strip())
            if self.nb_drones <= 0:
                raise ValueError("[DRONE] nb_drones must be a"
                                 " positive integer")

            for line in lines[1:]:
                prefix, details = line.split(":")
                prefix = prefix.strip()
                content, metadata = self.fetch_metadata(details)
                settings = content.split()

                if prefix in ("hub", "start_hub", "end_hub"):
                    if len(settings) != 3:
                        raise ValueError("[HUB] The format is not as expected")

                    self.generate_hub(prefix, settings[0],
                                      settings[1], settings[2], metadata)

                elif prefix in ("connection"):
                    if len(settings) != 1:
                        raise ValueError("[CONNECTION] The argument must "
                                         "be given as: 'name_1-name_2'")

                    self.generate_connection(settings[0], metadata)

        except Exception as e:
            print(f"[ERROR][PARSER]{e}")
            sys.exit(1)

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
            print("[HUB] Hub name must not contains '-'.")
            sys.exit(1)
        if name_hub in self.hubs:
            print(f"[HUB] Hub called {name_hub} already register.")
            sys.exit(1)

        pos: tuple[int, int] = (int(row), int(col))

        zone_data = metadata.get("zone", ZoneType.NORMAL.value).upper()
        zone = zone_data
        if hasattr(ZoneType, zone_data):
            zone = getattr(ZoneType, zone)
        else:
            raise ValueError(f"[ZONETYPE] {zone_data} Zone type unknown")

        color_data = metadata.get("color", "white").upper()
        if hasattr(Color, color_data):
            color_found = getattr(Color, color_data)
        else:
            raise ValueError(f"[COLOR] {color_data} unknown, make sure to "
                             "write on lowercase.")

        max_drones_hub = int(metadata.get("max_drones", 1))
        if prefix == "start_hub":
            max_drones_hub = self.nb_drones
        elif prefix == "end_hub":
            max_drones_hub = self.nb_drones
        drones_init: list[Drone] = []

        hub = Hub(
            name=name_hub,
            zone_type=zone,
            color=color_found,
            position=pos,
            drones=drones_init,
            max_drones=max_drones_hub
        )

        if prefix == "start_hub":
            hub.drones = [
                Drone(id=f"D{i}",
                      current_hub=pos) for i in range(
                          1, self.nb_drones + 1)]

        if prefix == "start_hub" and not self.start_hub:
            self.start_hub = hub
        elif prefix == "start_hub" and self.start_hub:
            raise ValueError("[HUB] There is already a start hub register.")

        if prefix == "end_hub" and not self.end_hub:
            self.end_hub = hub
        elif prefix == "end_hub" and self.end_hub:
            raise ValueError("[HUB] There is already an end hub register.")
        self.hubs.setdefault(name_hub, hub)

    def generate_connection(self, settings: str,
                            metadata: dict[str, str]) -> None:
        if "-" not in settings:
            raise ValueError("[CONNECTION] Names must be separate by '-'")
        names = settings.split("-")
        name_one = names[0].strip()
        name_two = names[1].strip()
        link_name = "-".join(sorted((name_one, name_two)))
        if link_name in self.connections:
            raise ValueError("[CONNECTION] Connection already register.")
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
        drones_init: list[Drone] = []
        connect = Connection(hub_name_a=name_one,
                             hub_name_b=name_two,
                             hubs=[hub_a, hub_b],
                             drones=drones_init,
                             max_link_capacity=max_capacity
                             )
        self.connections.setdefault(link_name, connect)
        self.connected_to.setdefault(name_one, []).append(name_two)
        self.connected_to.setdefault(name_two, []).append(name_one)
