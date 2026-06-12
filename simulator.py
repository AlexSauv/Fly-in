from utils import Drone
from parser import MapParser
from algorithm import PathFinder, Map


class Manager:
    def __init__(self, map_fly: Map):
        self.map_fly = map_fly
        self.pathfinder = PathFinder(map_fly)
        # self.hubs. = self.map_fly.hubs
        self.turn: int = 0
        self.drones_path: dict[str, list[str]] = {}
        self.reservation: dict[(str, int), int] = {}

    def drones_factory(self, path) -> None:
        for i in range(1, self.map_fly.nb_drones + 1):
            drone_id = f"D{i}"
            new_drone = Drone(id=drone_id, current_hub=self.map_fly.start_hub.position)
            self.map_fly.drones.append(new_drone)
            self.drones_path[drone_id] = list(path)

    
    def initiate_simulation(self) -> None:
        start = self.map_fly.start_hub.name
        end = self.map_fly.end_hub.name
        path = self.pathfinder.breadth_first_search(start, end)
        self.map_fly.drones = self.drones_factory(path)

    def simulation_turn(self) -> None:
        self.turn += 1
        turn_moves = []
        simulation = False
        for drone in self.map_fly.drones:
            next_step = self.drones_path[drone.id]
            if len(next_step) > 1:
                simulation = True
                current_pos = next_step.pop(0)
                current_hub = next_step[0]
                self.hubs[current_hub].drones.append()

                target = self.map_fly.hubs[current_hub]
                if map_fly.hubs[current_hub].drones < map_fly.hubs[current_hub].max_drones:
                    drone.moving_to(target.position)
                    map_fly.hubs[current_hub].drones.pop(drone)
                    map_fly.hubs[current_hub].drones += 1
                else:
                    print(f"Drone {drone.id} cannot move due to hub capacity")
                    print("hub", map_fly.hubs[current_hub].drones)
                turn_moves.append(f"{drone.id}-{current_hub}")
        if turn_moves:
            print(f"\n[Turn {self.turn}]\n")
            print("\n".join(turn_moves))
        return simulation
                
        

if __name__=="__main__":
    map_parsing = MapParser("maps/medium/02_circular_loop.txt")
    map_parsing.get_main_settings()
    map_fly = Map(map_parsing)
    simulation = Manager(map_fly)
    simulation.initiate_simulation()
    turn = True
    while turn:
        turn = simulation.simulation_turn()
        
    # print(simulation.drones)
    # print(simulation.drones_path)