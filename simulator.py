from algorithm import PathFinder, Map


class Manager:
    def __init__(self, map_fly: Map):
        self.map_fly = map_fly
        self.pathfinder = PathFinder(map_fly)
        self.turn: int = 0
        self.hub_reserve: dict[tuple[str, int], int] = {}
        self.link_reserve:  dict[tuple[str, int], int] = {}
        self.drones_path: dict[str, list[str]] = {}
        self.drone_step_index: dict[str, int] = {}
        self.cost = {"normal": 1,
                     "priority": 1,
                     'restricted': 2}

    def initiate_simulation(self) -> None:
        start = self.map_fly.start_hub.name
        end = self.map_fly.end_hub.name

        for drone in list(self.map_fly.hubs[start].drones):
            path = self.pathfinder.shortest_path(
                start, end, 0, self.hub_reserve,
                self.link_reserve)
            if not path:
                raise ValueError(f"[MANAGER] Path not found for {drone.id}.")

            self.drones_path[drone.id] = path
            self.drone_step_index[drone.id] = 0

            for (current_hub, current_turn), (next_hub, next_turn) in zip(
                    path, path[1:]):
                if next_hub != end and current_hub != end:
                    self.hub_reserve[
                        next_hub, next_turn] = self.hub_reserve.get(
                        (next_hub, next_turn), 0) + 1

                link = tuple(sorted((current_hub, next_hub)))
                for turn in range(current_turn, next_turn):
                    self.link_reserve[
                        (link, turn)] = self.link_reserve.get(
                            (link, turn), 0) + 1

    def simulation_turn(self) -> bool:
        self.turn += 1
        turn_moves = []

        drones_active = False
        for drone in self.map_fly.drones:
            path = self.drones_path[drone.id]
            step_index = self.drone_step_index.get(drone.id, 0)
            if step_index >= len(path) - 1:
                continue

            drones_active = True

            curr_hub_name, _ = path[step_index]
            next_hub_name, next_turn = path[step_index + 1]

            if self.turn < next_turn:
                # lk_tuple = tuple(sorted((curr_hub_name, next_hub_name)))
                # link_name = "-".join(lk_tuple)
                # turn_moves.append(f"{drone.id}-{link_name}")
                continue

            if self.turn == next_turn:

                current_hub = self.map_fly.hubs[curr_hub_name]
                next_hub = self.map_fly.hubs[next_hub_name]

                if drone in current_hub:
                    current_hub.drones.remove(drone)
                if drone not in next_hub:
                    next_hub.drones.append(drone)

                drone.moving_to(next_hub.position)
                turn_moves.append(f"{drone.id}-{next_hub_name}")
                self.drone_step_index[drone.id] += 1

        if turn_moves:
            print(f"\n[Turn {self.turn}]: " + " ".join(turn_moves))
            print(self.turn)
        return drones_active
