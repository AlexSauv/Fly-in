from algorithm import PathFinder, Map
from parser import MapParser

class Manager:
    def __init__(self, map_fly: Map):
        self.map_fly = map_fly
        self.pathfinder = PathFinder(map_fly)
        self.turn: int = 0
        self.planned_hub: dict[tuple[str, int], int] = {}
        self.planned_link:  dict[tuple[tuple[str, str], int], int] = {}
        self.drones_path: dict[str, list[str]] = {}
        self.drone_step_index: dict[str, int] = {}
        self.all_drones = list(map_fly.drones)
        self.turn_moves: list[str] = []

    def initiate_simulation(self) -> None:
        start = self.map_fly.start_hub.name
        end = self.map_fly.end_hub.name

        for drone in list(self.map_fly.hubs[start].drones):
            path = self.pathfinder.djikstra(
                start, end, 0, self.planned_hub,
                self.planned_link)
            if not path:
                raise ValueError(f"[MANAGER] Path not found for {drone.id}.")

            self.drones_path[drone.id] = path
            self.drone_step_index[drone.id] = 0

            for (current_hub, current_turn), (next_hub, next_turn) in zip(
                    path, path[1:]):
                if next_hub != end and current_hub != end:
                    self.planned_hub[
                        next_hub, next_turn] = self.planned_hub.get(
                        (next_hub, next_turn), 0) + 1

                link = tuple(sorted((current_hub, next_hub)))
                for turn in range(current_turn, next_turn):
                    self.planned_link[
                        (link, turn)] = self.planned_link.get(
                            (link, turn), 0) + 1

    def simulation_turn(self) -> bool:
        turn_moves = []
        end_name = self.map_fly.end_hub.name
        drones_active = any(drone not in self.map_fly.hubs[end_name].drones
                            for drone in self.all_drones)
        if not drones_active:
            return False

        self.turn += 1
        for drone in self.all_drones:
            path = self.drones_path[drone.id]
            step_index = self.drone_step_index.get(drone.id, 0)
            if step_index >= len(path) - 1:
                continue

            curr_hub_name, _ = path[step_index]
            next_hub_name, next_turn = path[step_index + 1]

            if self.turn < next_turn:
                continue

            if self.turn == next_turn:
                current_hub = self.map_fly.hubs[curr_hub_name]
                next_hub = self.map_fly.hubs[next_hub_name]

                if curr_hub_name != next_hub_name:
                    if drone in current_hub.drones:
                        current_hub.drones.remove(drone)
                    if drone not in next_hub.drones:
                        next_hub.drones.append(drone)
                    drone.moving_to(next_hub.position)
                    turn_moves.append(f"{drone.id}-{next_hub_name}")
                self.drone_step_index[drone.id] += 1

        if turn_moves:
            print(f"\n[Turn {self.turn}]: " + " ".join(turn_moves))
            print(self.turn)
        return drones_active

if __name__ == "__main__":
        map_parsing = MapParser("maps/medium/03_priority_puzzle.txt")
        map_parsing.get_main_settings()
        map_fly = Map(map_parsing)

        simulation = Manager(map_fly)
        simulation.initiate_simulation()
        while simulation.simulation_turn():
            pass