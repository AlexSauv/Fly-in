
import sys
try:
    from enum import Enum
    from typing import Optional
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
    CYAN = "36"
    BLUE = "34"
    GREEN = "38;2;34;139;34"
    RED = "38;5;88"
    YELLOW = '38;5;184'
    DARK_PINK = '38;5;176'
    BLACk = '38;5;232'
    BROWN = '38;5;94'
    PURPLE = '38;5;54'


class Drone(BaseModel):
    id: str
    current_hub: tuple[int, int]

    def moving_to(self, next_hub: tuple[int, int]) -> None:
        self.current_hub = next_hub


class Hub(BaseModel):
    name: str = Field(min_length=2, max_length=10)
    zone_type: str = Field(default=ZoneType.NORMAL.value)
    color: Optional[str] = Field(default=Color.GREEN.value)
    position: tuple[int, int]
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
