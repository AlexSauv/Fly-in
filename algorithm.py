from parser import MapParser
import heapq


class Map:
    def __init__(self, settings: MapParser):
        self.start_hub = settings.start_hub
        self.end_hub = settings.end_hub
        self.drones = self.start_hub.drones
        self.nb_drones = settings.nb_drones
        self.hubs = settings.hubs
        self.connections = settings.connections
        self.connected_to = settings.connected_to


class PathFinder:
    def __init__(self, map: Map):
        self.map = map
        self.cost_turn = {"normal": 1,
                          "priority": 1,
                          'restricted': 2}

    def djikstra(self, start: str, end: str, turn: int,
                 reserve: dict[tuple[str, int], int],
                 link_reserve: dict[tuple[
                     tuple[str, str], int], int]) -> list[str]:

        visited = set()
        waiting: list[tuple[int, int, str, list[tuple[str, int]]]] = [
            (turn, 0, start, [(start, turn)])
        ]

        while waiting:

            curr_turn, priority, hub_name, path = heapq.heappop(waiting)
            if hub_name == end:
                return path

            current_state = (hub_name, curr_turn)
            if current_state in visited:
                continue
            visited.add(current_state)

            next_hubs = self.map.connected_to.get(hub_name, [])
            for next_name in next_hubs:
                neighbor = self.map.hubs[next_name]
                if neighbor.zone_type == "blocked":
                    continue

                zone_cost = self.cost_turn.get(neighbor.zone_type, 1)
                next_turn = curr_turn + zone_cost

                move_priority = 0 if neighbor.zone_type == "priority" else 1
                next_priority = priority + move_priority
                hub_ok = (next_name in (start, end) or
                          reserve.get((next_name, next_turn
                                       ), 0) < neighbor.max_drones)

                link = tuple(sorted((hub_name, next_name)))

                link_name = "-".join(link)
                if self.map.connections[link_name]:
                    lk_cap = self.map.connections[link_name].max_link_capacity

                link_approved = max([link_reserve.get((link, turn), 0)
                                    for turn in range(
                                        curr_turn, next_turn)]) < lk_cap

                if hub_ok and link_approved:
                    heapq.heappush(waiting, (next_turn,
                                             next_priority,
                                             next_name,
                                             path + [(next_name, next_turn)]))

            if hub_name != end:
                current_hub_stay = self.map.hubs[hub_name]
                next_turn_stay = curr_turn + 1
                available_stay = reserve.get((hub_name,
                                              next_turn_stay), 0)

                if (hub_name == start or
                        available_stay < current_hub_stay.max_drones):
                    heapq.heappush(waiting, (next_turn_stay,
                                             priority + 1,
                                             hub_name,
                                             path + [(hub_name,
                                                      next_turn_stay)]))
        return []
