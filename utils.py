
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, model_validator, ValidationError


class Zone_Type(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Color(Enum):
    GREEN = "32"
    RED = "31"
    CYAN = "36"
    PURPLE = "35"
    BLUE = "34"
    GREEN_GRASS = "38;2;34;139;34"
    RED_WINE = "38;5;88"
    GOLD = '38;5;184'
    DARK_PINK = '38;5;176'
    BLACk = '38;5;232'
    BROWN = '38;5;94'
    DARK_PURPLE = '38;5;54'


class Drone(BaseModel):
    id: str
    current_hub: tuple[int, int]

    def moving_to(self, next_hub: tuple[int, int]) -> None:
        self.current_hub = next_hub


class Hub(BaseModel):
    name: str = Field(min_length=2, max_length=10)
    zone_type: str = Field(default=Zone_Type.NORMAL.value)
    color: Optional[str] = Field(default=None)
    position: tuple[int, int] = Field(default=None)
    max_drones: int = Field(default=1, ge=1)


class Connection(BaseModel):
    hub_name_a: str = Field(min_length=1)
    hub_name_b: str = Field(min_length=1)
    zones: list[Hub] = Field(ge=2)
    max_link_capacity: Optional[int] = Field(ge=1, default=1)

    @model_validator(mode="after")
    def check_name(self) -> self:
        if self.hub_name_a == self.hub_name_b:
            raise ValueError("[Error] Both hub names must differ.")
        return self
