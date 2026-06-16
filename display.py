import arcade
from algorithm import Map
from parser import MapParser
from simulator import Manager


class MapDisplay(arcade.Window):
    def __init__(self, width, height, title, simulation: Manager):
        self.simulation = simulation
        self.map_fly = simulation.map_fly
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.DARK_BLUE)

    def get_center(self) -> tuple[int, int]:
        hubs = map_fly.hubs

        min_x = min([hubs[hub].position[0] for hub in hubs])
        min_y = min([hubs[hub].position[1] for hub in hubs])
        max_x = max([hubs[hub].position[0] for hub in hubs])
        max_y = max([hubs[hub].position[1] for hub in hubs])

        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2

        offset_x = (self.width / 2) - (center_x * 150)
        offset_y = (self.height / 2) - (center_y * 150)

        return offset_x, offset_y

    def on_draw(self):
        self.clear()
        hubs = map_fly.hubs
        connections = map_fly.connections

        center_x, center_y = self.get_center()
        for connection in connections:
            hub_start = connections[connection].hubs[0]
            hub_end = connections[connection].hubs[1]

            start_x = hub_start.position[0] * 150 + center_x
            start_y = hub_start.position[1] * 150 + center_y

            end_x = hub_end.position[0] * 150 + center_x
            end_y = hub_end.position[1] * 150 + center_y
            arcade.draw_line(start_x, start_y, end_x, end_y,
                             arcade.color.WHITE, 3)
        for hub in hubs:
            x = hubs[hub].position[0] * 150 + center_x
            y = hubs[hub].position[1] * 150 + center_y
            color = hubs[hub].color.upper()
            if color.startswith("#"):
                hex_val = color.lstrip("#")
                color_rgb = (int(hex_val[0:2], 16),
                             int(hex_val[2:4], 16),
                             int(hex_val[4:6], 16))
                arcade.draw_circle_filled(x, y, 35, color_rgb)
            elif hasattr(arcade.color, color):
                color_rgb = getattr(arcade.color, color)
                arcade.draw_circle_filled(x, y, 35, color_rgb)
            else:
                raise ValueError(f"[DISPLAY] {color} color not found")



if __name__ == "__main__":
    try:
        map_parsing = MapParser("maps/challenger/01_the_impossible_dream.txt")
        map_parsing.get_main_settings()
        map_fly = Map(map_parsing)

        simulation = Manager(map_fly)
        simulation.initiate_simulation()
        while simulation.simulation_turn():
            pass
        renderer = MapDisplay(3800, 2100, "Fly-in", simulation)
        arcade.run()
        print(simulation.turn)
    except Exception as e:
        print(e)
