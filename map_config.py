
import sys
try:
    import re
    from enum import Enum
    from typing_extensions import Self, Optional
    from pydantic import BaseModel, Field, model_validator
    from parser import FileParser
except ImportError:
    print("Make sure to use: - make install before - make run")
    sys.exit(1)


class ZoneType(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Color(Enum):
    CYAN = "cyan"
    BLUE = "#1624a6"
    GREEN = "#2fa029"
    RED = "#c72712"
    YELLOW = '#d6c11e'
    PINK = 'pink'
    BLACK = 'black'
    ORANGE = '#db882a'
    PURPLE = 'purple'
    BROWN = 'brown'
    MAROON = '#633c0f'
    GOLD = '#ab8f03'
    WHITE = "white"
    DARKRED = '#8B0000'
    VIOLET = '#ae3ede'
    CRIMSON = 'crimson'
    RAINBOW = 'rainbow'
    LIME = '#00FF00'
    MAGENTA = '#FF00FF'


class Hub(BaseModel):
    """ Create a class for zone based on pydantic model """
    name: str = Field(min_length=2, max_length=30)
    zone_type: str = Field(default=ZoneType.NORMAL.value)
    color: str = Field(default=Color.GREEN.value)
    position: tuple[int, int]
    drones: list[int] = Field(default_factory=list)
    max_drones: int = Field(default=1, ge=1)


class Connection(BaseModel):
    """ Create a class for connection
    between zones based on pydantic model """
    hub_name_a: str = Field(min_length=1)
    hub_name_b: str = Field(min_length=1)
    hubs: list[Hub] = Field(max_length=2)
    max_link_capacity: int = Field(ge=1, default=1)
    drones: list[int] = Field(default_factory=list)

    @model_validator(mode="after")
    def check_name(self) -> Self:
        if self.hub_name_a == self.hub_name_b:
            raise ValueError("[Error] Both hub names must differ.")
        return self


class MapConfig:
    """ Create Map OOP for handle each details of the map, regrouping hubs,
      drones, connections and data for each of them """
    def __init__(self, settings: FileParser):
        self.settings = settings.fetch_infos()
        self.map_name = settings.name_file.split(
            "/")[-1].removesuffix(".txt")
        self.nb_drones = 0
        self.start_hub: Optional[Hub] = None
        self.end_hub: Optional[Hub] = None
        self.hubs: dict[str, Hub] = {}
        self.connections: dict[str, Connection] = {}
        self.connected_to: dict[str, list[str]] = {}

    def generate_map(self) -> None:
        """ This function set all data combines for hubs,
            connections, number of drones in the object.
            it splits line by line each prefix, content
            and metadata in order to create
            hubs and connections given

            return: Return nothing but set the right data in the object
        """
        lines: list[str] = self.settings
        if not lines[0].startswith("nb_drones:"):
            raise ValueError(" [CONFIG] must begin"
                             " with nb_drones:int")

        self.nb_drones = int(lines[0].split(":")[1].strip())
        if self.nb_drones <= 0:
            raise ValueError("[DRONE] nb_drones must"
                             " be a positive integer")

        for line in lines[1:]:
            prefix, details = line.split(":")
            prefix = prefix.strip()
            content, metadata = self.metadata(details)
            config = content.split()

            if prefix in ("hub", "start_hub", "end_hub"):
                if len(config) != 3:
                    raise ValueError("[HUB] The format is not as expected")

                self.generate_hub(prefix,
                                  config[0],
                                  config[1],
                                  config[2],
                                  metadata)

            elif prefix in ("connection"):
                if len(config) != 1:
                    raise ValueError("[CONNECTION] The argument must "
                                     "be given as: 'name_1-name_2'")

                self.generate_connection(config[0], metadata)
        if not self.start_hub:
            raise ValueError("[HUB] No start has been register")
        if not self.end_hub:
            raise ValueError("[HUB] No end has been register")

    def metadata(self, config: str) -> tuple[str, dict[str, str]]:
        """ This function is used for handling metadata fetch from file
        for each hubs and connections

        args: config is regrouping main content and metadata for each line

        return: It returns a tuple with the main content split from metadata
        and each metadata details for specificity
        """
        meta_data: dict[str, str] = {}
        match = re.search(r'\[(.*?)\]', config)

        if match:
            meta_content = match.group(1)
            if not meta_content:
                raise ValueError("[METADATA] Metadata format not respected")
            meta_details = ["zone", "color", "max_drones", "max_link_capacity"]
            main_content = config.replace(match.group(0), '').strip()
            for part in meta_content.split():
                if "=" not in part:
                    raise ValueError("[METADARA] must be '[details=infos]'")
                key, value = part.split("=")
                if key not in meta_details:
                    raise ValueError(f"[METADATA] {key} key is unknown")
                meta_data[key] = value
        else:
            main_content = config
            meta_content = None
        return main_content, meta_data

    def generate_hub(self, prefix: str,
                     name_hub: str,
                     row: str,
                     col: str,
                     metadata: dict[str, str]) -> None:
        """
        This function is used as hub factory,
        it create each hubs mentionned in the file
        read with all specificity given
        It also set start and end hub

        args: prefix is for each type connections, hubs (start and end)
              name_hub is the name given of the hub
              row is the position from the width
              col is the position from the height
              metadata is the meta given from function metadata

        return: Return nothing just generate the hub
        """
        if "-" in name_hub:
            raise ValueError("[HUB] Hub name must not contains '-'.")
        if name_hub in self.hubs:
            raise ValueError(f"[HUB] Hub called {name_hub} already register.")

        drones_init: list[int] = []
        pos: tuple[int, int] = (int(row), int(col))
        zone_data = metadata.get("zone", ZoneType.NORMAL.value).upper()
        zone = zone_data
        color_data = metadata.get("color", "white").upper()
        max_drones_hub = int(metadata.get("max_drones", 1))

        if hasattr(ZoneType, zone_data):
            zone = getattr(ZoneType, zone)
        else:
            raise ValueError(f"[ZONETYPE] {zone_data} Zone type unknown")

        if hasattr(Color, color_data):
            color_found = getattr(Color, color_data)
        else:
            raise ValueError(f"[COLOR] {color_data} unknown")

        if prefix == "start_hub":
            max_drones_hub = self.nb_drones
        elif prefix == "end_hub":
            max_drones_hub = self.nb_drones

        hub = Hub(
            name=name_hub,
            zone_type=zone,
            color=color_found,
            position=pos,
            drones=drones_init,
            max_drones=max_drones_hub
        )

        if prefix == "start_hub":
            hub.drones = [i for i in range(
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

    def generate_connection(self,
                            settings: str,
                            metadata: dict[str, str]) -> None:
        """
        This function is used as connection factory,
        it create each connections mentionned in the file
        read with all specificity given

        args: settings are the main content of
              each line were prefix is connection
              it gives hubs related to each other
              metadata is the meta given from function metadata and
              contains specifity for the connection

        return: Return nothing just generate the connection
        """
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
        drones_init: list[int] = []
        connect = Connection(hub_name_a=name_one,
                             hub_name_b=name_two,
                             hubs=[hub_a, hub_b],
                             drones=drones_init,
                             max_link_capacity=max_capacity
                             )
        self.connections.setdefault(link_name, connect)
        self.connected_to.setdefault(name_one, []).append(name_two)
        self.connected_to.setdefault(name_two, []).append(name_one)
