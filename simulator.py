from utils import Drone
from parser import MapParser
from algorithm import PathFinder

class Manager:
    def __init__(self, settings: MapParser):
        self.settings = settings
        self.pathfinder = PathFinder(settings)
        self.drones: list[Drone] = []
        self.turn: int = 0
        self.drones_path: dict[str, list[str]] = {}

    def drones_factory(self, path) -> None:
        for i in range(1, self.settings.nb_drones + 1):
            drone_id = f"D{i}"
            new_drone = Drone(id=drone_id, current_hub=self.settings.start_hub.position)
            self.drones.append(new_drone)
            self.drones_path[drone_id] = list(path)
    
    def initiate_simulation(self) -> None:
        start = self.settings.start_hub.name
        end = self.settings.end_hub.name
        path = self.pathfinder.breadth_first_search(start, end)
        self.drones_factory(path)

    def simulation_turn(self) -> None:
        self.turn += 1
        turn_moves = []
        simulation = False
        for drone in self.drones:
            next_step = self.drones_path[drone.id]
            if len(next_step) > 1:
                simulation = True
                current_pos = next_step.pop(0)
                current_hub = next_step[0]

                target = self.settings.hubs[current_hub]
                drone.moving_to(target.position)
                turn_moves.append(f"{drone.id}-{current_hub}")
        if turn_moves:
            print(f"\n[Turn {self.turn}]\n")
            print("\n".join(turn_moves))
        return simulation
                
        

if __name__=="__main__":
    map_parsing = MapParser("maps/medium/02_circular_loop.txt")
    map_parsing.get_main_settings()
    simulation = Manager(map_parsing)
    simulation.initiate_simulation()
    turn = True
    while turn:
        turn = simulation.simulation_turn()
    # print(simulation.drones)
    # print(simulation.drones_path)