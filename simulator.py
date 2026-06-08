from utils import Drone
from parser import MapParser
from algorithm import PathFinder

class Manager:
    def __init__(self, settings: MapParser):
        self.settings = settings
        self.pathfinder = PathFinder(settings)
        self.drones: list[Drone] = []
        self.turn: int = 0

    def drones_factory(self) -> None:
        for i in range(1, self.settings.nb_drones + 1):
            drone_id = f"D{i}"
            new_drone = Drone(id=drone_id, current_hub=self.settings.start_hub.position)
            self.drones.append(new_drone)

if __name__=="__main__":
    map_parsing = MapParser("maps/medium/02_circular_loop.txt")
    map_parsing.get_main_settings()
    simulation = Manager(map_parsing)
    simulation.drones_factory()
    print(len(simulation.drones))
    for drone in simulation.drones:
        print(drone.id)