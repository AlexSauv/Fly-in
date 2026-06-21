
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
    BLUE = "#1624a6"
    GREEN = "#17ad10"
    RED = "#c72712"
    YELLOW = '#d6c11e'
    PINK = 'pink'
    BLACK = 'black'
    ORANGE = '#db882a'
    PURPLE = 'purple'
    BROWN = 'brown'
    MAROON = '#633c0f'
    GOLD = '#ab8f03'
    DARKRED = '#8B0000'
    VIOLET = '#ae3ede'
    CRIMSON = 'crimson'
    RAINBOW = 'rainbow'


class Hub(BaseModel):
    name: str = Field(min_length=2, max_length=30)
    zone_type: str = Field(default=ZoneType.NORMAL.value)
    color: str = Field(default=Color.GREEN.value)
    position: tuple[int, int]
    drones: list[str] = Field(default=list)
    max_drones: int = Field(default=1, ge=1)


class Connection(BaseModel):
    hub_name_a: str = Field(min_length=1)
    hub_name_b: str = Field(min_length=1)
    hubs: list[Hub] = Field(max_length=2)
    max_link_capacity: int = Field(ge=1, default=1)
    drones: list[str] = Field(default=list)

    @model_validator(mode="after")
    def check_name(self) -> Self:
        if self.hub_name_a == self.hub_name_b:
            raise ValueError("[Error] Both hub names must differ.")
        return self
