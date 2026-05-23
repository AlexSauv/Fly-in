

class Drone:
    def ___init__(self, drone_id: str, current_hub: tuple[int, int]):
        self.drone_id = drone_id,
        self.current_hub = current_hub

    def moving_to(self, next_hub: tuple[int, int]) -> None:
        self.current_hub = next_hub


class Hub:
    def __init__(self, name: str, pos: tuple[int, int],
                 zone_type: str = "normal", capacity: int = 1) -> None:
        self.name = name
        self.pos = pos
        self.zone_type = zone_type
        self.capacity = capacity
        self.drones: list[Drone] = []


class Connection:
    def __init__(self, hub_a: Hub, hub_b, max_capacity: int = 1):
        self.hub_a = hub_a
        self.hub_b = hub_b
        self.max_capacity = max_capacity
        self.current_drones: int = 0

