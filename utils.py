
import sys
try:
    from enum import Enum
    from typing_extensions import Self
    from pydantic import BaseModel, Field, model_validator
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
    BLUE = "blue"
    GREEN = "green"
    RED = "red"
    YELLOW = 'yellow'
    PINK = 'pink'
    BLACK = 'black'
    ORANGE = 'orange'
    PURPLE = 'purple'
    BROWN = 'brown'
    MAROON = 'maroon'
    GOLD = 'gold'
    DARKRED = '#8B0000'
    VIOLET = 'violet'
    CRIMSON = 'crimson'
    RAINBOW = 'rainbow'


class Drone(BaseModel):
    id: str
    current_hub: tuple[int, int]

    def moving_to(self, next_hub: tuple[int, int]) -> None:
        self.current_hub = next_hub


class Hub(BaseModel):
    name: str = Field(min_length=2, max_length=30)
    zone_type: str = Field(default=ZoneType.NORMAL.value)
    color: str = Field(default=Color.GREEN.value)
    position: tuple[int, int]
    drones: list[Drone] = Field(default=list)
    max_drones: int = Field(default=1, ge=1)


class Connection(BaseModel):
    hub_name_a: str = Field(min_length=1)
    hub_name_b: str = Field(min_length=1)
    hubs: list[Hub] = Field(max_length=2)
    max_link_capacity: int = Field(ge=1, default=1)

    @model_validator(mode="after")
    def check_name(self) -> Self:
        if self.hub_name_a == self.hub_name_b:
            raise ValueError("[Error] Both hub names must differ.")
        return self
