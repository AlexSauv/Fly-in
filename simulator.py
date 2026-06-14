from utils import Drone
from parser import MapParser
from algorithm import PathFinder, Map
import sys


class Manager:
    def __init__(self, map_fly: Map):
        self.map_fly = map_fly
        self.pathfinder = PathFinder(map_fly)
        self.turn: int = 0
        self.reservation: dict[tuple[str, int], int] = {}
        self.link_reservation:  dict[tuple[str, int], int] = {}
        self.drones_path: dict[str, list[str]] = {}
        self.cost = {"normal": 1,
                     "priority": 1,
                     'restricted': 2}


    def initiate_simulation(self) -> None:
        start = self.map_fly.start_hub.name
        end = self.map_fly.end_hub.name

        for drone in self.map_fly.hubs[start].drones:
            path = self.pathfinder.shortest_path(
                start, end, 0, self.reservation,
                  self.link_reservation)
            if not path:
                raise ValueError(f"[MANAGER] Path not found for {drone.id}.")

            self.drones_path[drone.id] = [hub for hub, _ in path]

            for (current_hub, current_turn), (next_hub, next_turn) in zip(path, path[1:]):
                if next_hub != end and current_hub != end:
                    self.reservation[next_hub, next_turn] = self.reservation.get((next_hub, next_turn), 0) + 1
            
                link = tuple(sorted(current_hub, next_hub))
                for turn in range(current_turn, next_turn):
                    self.link_reservation[(link, turn)] = self.link_reservation((link, turn), 0) + 1

    def simulation_turn(self) -> bool:
        self.turn += 1
        turn_moves = []

        drone_active = 0
        for drone in self.map_fly.drones:
            next_step = self.drones_path[drone.id]
            if len(next_step) > 1:
                drone_active += 1

                current_hub_name = next_step[0]
                next_hub_name = next_step[1]

                current_hub = self.map_fly.hubs[current_hub_name]
                next_hub = self.map_fly.hubs[next_hub_name]

                if drone in current_hub.drones:
                    current_hub.drones.remove(drone)
                if drone not in next_hub.drones:
                    next_hub.drones.append(drone)
                drone.moving_to(next_hub.position)
                turn_moves.append(f"{drone.id}-{next_hub_name}")
            self.drones_path[drone.id].pop(0)

        if turn_moves:
            print(f"\n[Turn {self.turn}]: " + " ".join(turn_moves))
        return drone_active > 0
                
        

if __name__=="__main__":
    try:
        map_parsing = MapParser("maps/medium/02_circular_loop.txt")
        map_parsing.get_main_settings()
        map_fly = Map(map_parsing)
        simulation = Manager(map_fly)
        simulation.initiate_simulation()
        turn = True
        while turn:
            print("\nSimulation terminée. Position finale des drones :")
            for hub_name, hub in simulation.map_fly.hubs.items():
                if hub.drones:
                    print(f"Hub {hub_name} contient : {[d.id for d in hub.drones]}\n")
            turn = simulation.simulation_turn()
    except Exception as e:
        print(e)
        
    # print(simulation.drones)
    # print(simulation.drones_path)