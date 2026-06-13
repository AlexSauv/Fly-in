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
        self.drones_path: dict[str, list[str]] = {}
        self.cost = {"normal": 1,
                     "priority": 1,
                     'restricted': 2}


    def initiate_simulation(self) -> None:
        start = self.map_fly.start_hub.name
        end = self.map_fly.end_hub.name

        for drone in self.map_fly.hubs[start].drones:
            path = self.pathfinder.shortest_path(
                start, end, 0, self.reservation)
            self.drones_path[drone.id] = list(path)

            current_turn = 0
            self.reservation[
                (start, current_turn)] = self.reservation.get(
                (start, current_turn), 0) + 1

            for i in range(len(path) - 1):
                current_hub_name = path[i]
                next_hub_name = path[i + 1]

                if current_hub_name == next_hub_name:
                    cost = 1

                else:
                    zone_cost = self.map_fly.hubs[next_hub_name].zone_type
                    cost = self.cost.get(zone_cost, 1)
                current_turn += cost
                self.reservation[
                    (next_hub_name, current_turn)] = self.reservation.get(
                    (next_hub_name, current_turn), 0) + 1
            print( drone.id, path)

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

                if current_hub_name == next_hub_name:
                    next_step.pop(0)

                else:
                    if drone in current_hub.drones:
                        current_hub.drones.remove(drone)
                    if drone not in next_hub.drones:
                        next_hub.drones.append(drone)
                    drone.moving_to(next_hub.position)
                    turn_moves.append(f"{drone.id}-{next_hub_name}")
                    next_step.pop(0)

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
            print("Simulation terminée. Position finale des drones :")
            for hub_name, hub in simulation.map_fly.hubs.items():
                if hub.drones:
                    print(f"Hub {hub_name} contient : {[d.id for d in hub.drones]}")
            turn = simulation.simulation_turn()
    except Exception as e:
        print(e)
        
    # print(simulation.drones)
    # print(simulation.drones_path)