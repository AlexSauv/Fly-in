import arcade
from algorithm import Map
from parser import MapParser
from simulator import Manager


class MapDisplay(arcade.Window):
    def __init__(self, width, height, title, simulation: Manager):
        self.simulation = simulation
        self.map_fly = simulation.map_fly
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.BLACK)

    def get_center(self) -> tuple[int, int]:
        hubs = map_fly.hubs

        min_x = min([hubs[hub].position[0] for hub in hubs])
        min_y = min([hubs[hub].position[1] for hub in hubs])
        max_x = max([hubs[hub].position[0] for hub in hubs])
        max_y = max([hubs[hub].position[1] for hub in hubs])

        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2

        offset_x = (self.width / 2) - (center_x * 175)
        offset_y = (self.height / 2) - (center_y * 175)

        return offset_x, offset_y

    def on_draw(self):
        self.clear()
        hubs = map_fly.hubs

        center_x, center_y = self.get_center()
        for hub in hubs:
            x = hubs[hub].position[0] * 175 + center_x
            y = hubs[hub].position[1] * 175 + center_y
            color = hubs[hub].color.upper()
            if color.startswith("#"):
                hex_val = color.lstrip("#")
                color_rgb = (int(hex_val[0:2], 16),
                             int(hex_val[2:4], 16),
                             int(hex_val[4:6], 16))
                arcade.draw_circle_filled(x, y, 40, color_rgb)
            elif hasattr(arcade.color, color):
                color_rgb = getattr(arcade.color, color)
                arcade.draw_circle_filled(x, y, 40, color_rgb)
            else:
                raise ValueError(f"[DISPLAY] {color} color not found")


if __name__ == "__main__":
    try:
        map_parsing = MapParser("maps/challenger/01_the_impossible_dream.txt")
        map_parsing.get_main_settings()
        map_fly = Map(map_parsing)

        simulation = Manager(map_fly)
        simulation.initiate_simulation()
        renderer = MapDisplay(3800, 2100, "Fly-in", simulation)
        arcade.run()
    except Exception as e:
        print(e)
