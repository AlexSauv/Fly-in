from map_config import MapConfig, ZoneType
import heapq


class PathFinder:
    def __init__(self, map_config: MapConfig):
        self.map_config = map_config
        self.cost_turn = {ZoneType.NORMAL: 1,
                          ZoneType.PRIORITY: 1,
                          ZoneType.RESTRICTED: 2}

    def dijkstra_algo(self, start: str, end: str, turn: int,
                      planned_hub: dict[tuple[str, int], int],
                      planned_link: dict[tuple[
                          tuple[str, str], int],
                          int]) -> list[tuple[str, int]]:
        """
        Finds the shortest time-dependent path between two hubs using Dijkstra
        algorithm.

        Args:
            start: Name of the start hub.
            end: Name of the dest hub.
            turn: Starting turn/time-step.
            planned_hub: Current drone occupancy per hub and turn.
            planned_link: Current drone traffic per link and turn.

        Returns:
            A list of (hub_name, turn) tuples representing
            the path, or [] if no path found.
        """
        visited = set()
        waiting: list[tuple[int, float, str, list[tuple[str, int]]]] = [
            (turn, 0, start, [(start, turn)])
        ]
        limit_turn = self.map_config.nb_drones * 5

        while waiting:
            curr_turn, priority, hub_name, path = heapq.heappop(waiting)
            if curr_turn > limit_turn:
                return []
            if hub_name == end:
                return path

            current_state = (hub_name, curr_turn)
            if current_state in visited:
                continue
            visited.add(current_state)

            next_hubs = self.map_config.connected_to.get(hub_name, [])
            for next_name in next_hubs:

                neighbor = self.map_config.hubs[next_name]
                if neighbor.zone_type == ZoneType.BLOCKED:
                    continue

                zone_cost = self.cost_turn.get(neighbor.zone_type)
                if zone_cost:
                    next_turn = curr_turn + zone_cost

                if (next_name not in (start, end) and
                        planned_hub.get((next_name, next_turn),
                                        0) >= neighbor.max_drones):
                    continue

                move_priority = (0.5 if neighbor.zone_type == ZoneType.PRIORITY
                                 else self.cost_turn[neighbor.zone_type])
                next_priority = priority + move_priority

                hub_one, hub_two = sorted((hub_name, next_name))
                link = (hub_one, hub_two)
                link_name = "-".join(link)

                lk_cap = 1
                if self.map_config.connections[link_name]:
                    lk_cap = self.map_config.connections[
                        link_name].max_link_capacity

                link_approved = all(planned_link.get((link, t), 0) < lk_cap
                                    for t in range(curr_turn, next_turn))

                if link_approved:
                    heapq.heappush(waiting, (next_turn,
                                             next_priority,
                                             next_name,
                                             path + [(next_name,
                                                      next_turn)]))

            if hub_name != end:
                current_hub_stay = self.map_config.hubs[hub_name]
                next_turn_stay = curr_turn + 1
                available_stay = planned_hub.get((hub_name,
                                                  next_turn_stay), 0)

                if (hub_name == start or
                        available_stay < current_hub_stay.max_drones):
                    heapq.heappush(waiting, (
                                             next_turn_stay,
                                             priority + 0.5,
                                             hub_name,
                                             path + [(hub_name,
                                                      next_turn_stay)]))
        return []
