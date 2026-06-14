from collections import deque
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
        self.cost = {"normal": 1,
                     "priority": 1,
                     'restricted': 2}

    def shortest_path(self, start: str, end: str, turn: int,
                      reservation: dict[tuple[str, int], int],
                      link_reservation: dict[tuple[tuple[str, str], int], int]) -> list[str]:

        visited = set()
        waiting = [(0, turn, start, [(start, turn)])]

        while waiting:

            cost, current_turn, current_hub_name, path = heapq.heappop(waiting)
            if current_hub_name == end:
                return path

            current_state = (current_hub_name, current_turn)
            if current_state in visited:
                continue
            visited.add(current_state)

            next_hubs = self.map.connected_to.get(current_hub_name, [])
            for next_hub_name in next_hubs:
                neighbor = self.map.hubs[next_hub_name]
                if neighbor.zone_type == "blocked":
                    continue

                zone_cost = self.cost.get(neighbor.zone_type, 1)
                next_turn = current_turn + zone_cost
                hub_approved = (next_hub_name in (start, end) or 
                                reservation.get((next_hub_name,
                                                  next_turn), 0)
                                                    < neighbor.max_drones)
                
                link = tuple(sorted((current_hub_name, next_hub_name)))

                link_capacity = 1
                link_name = "-".join(link)
                if self.map.connections[link_name]:
                    link_capacity = self.map.connections[link_name].max_link_capacity

                link_approved = max(link_reservation.get(link, turn) 
                                    for turn in range(current_turn, next_turn)) < link_capacity

                if hub_approved and link_approved:
                    new_cost = cost + zone_cost
                    if neighbor.zone_type == "priority":
                        new_cost -= 0.5
                    heapq.heappush(waiting, (new_cost, next_turn,
                                             next_hub_name,
                                             path + [(next_hub_name, next_turn)]))

            if current_hub_name != end:
                current_hub_stay = self.map.hubs[current_hub_name]
                next_turn_stay = current_turn + 1
                available_stay = reservation.get((current_hub_name,
                                                  next_turn_stay), 0)

                if (current_hub_name == start or
                        available_stay < current_hub_stay.max_drones):
                    heapq.heappush(waiting, (cost + 1, next_turn_stay,
                                             current_hub_name,
                                             path + [(current_hub_name, next_turn_stay)]))
        return []


if __name__=="__main__":
    map_set = MapParser("maps/medium/02_circular_loop.txt")
    map_set.get_main_settings()
    map_fly = Map(map_set)
    algo = PathFinder(map_fly)
    res = algo.shortest_path(map_set.start_hub.name, map_set.end_hub.name)
    print(res)