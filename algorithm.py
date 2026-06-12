from collections import deque
from parser import MapParser
from utils import Drone

class Map:
    def __init__(self, settings: MapParser):
        self.nb_drones = settings.nb_drones
        self.drones: list[Drone] = []
        self.hubs = settings.hubs
        self.connections = settings.connections
        self.connected_to = settings.connected_to
        self.start_hub = settings.start_hub
        self.end_hub = settings.end_hub

class PathFinder:
    def __init__(self, map: Map):
        self.map = map

    def breadth_first_search(self, start: str, end: str) -> list[str]:
        waiting = deque([(start, [start])])
        visited = {start}

        while waiting:
            current_hub, path = waiting.popleft()
            next_hubs = self.map.connected_to.get(current_hub, [])
            for next in next_hubs:
                if next not in visited:
                    if next == end:
                        return path + [next]
                    visited.add(next)
                    waiting.append((next, path + [next]))
        return []
    
if __name__=="__main__":
    map_set = MapParser("maps/medium/02_circular_loop.txt")
    map_set.get_main_settings()
    algo = PathFinder(map_set)
    res = algo.breadth_first_search(map_set.start_hub.name, map_set.end_hub.name)
    print(res)