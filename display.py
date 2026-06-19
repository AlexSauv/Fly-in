import arcade
from algorithm import Map
from parser import MapParser
from simulator import Manager
import math


class MapDisplay(arcade.Window):
    def __init__(self, width, height, title, simulation: Manager):
        super().__init__(width, height, title)
        self.simulation = simulation
        self.map_fly = simulation.map_fly
        arcade.set_background_color(arcade.color.DARK_BLUE)
        self.drone_txt = arcade.load_texture("drone_one.png")
        self.drone_sprites = arcade.SpriteList()
        self.drone_speed = 5
        self.set_drone()

    def set_drone(self) -> None:
        center_x, center_y = self.get_center()
        self.drone_sprites.clear()
        hubs = self.map_fly.hubs
        for hub in hubs.values():
            if hub.drones:
                for drone_data in hub.drones:
                    drone_sprite = arcade.Sprite(self.drone_txt, scale=0.015)
                    drone_sprite.center_x = hub.position[0] * 150 + center_x
                    drone_sprite.center_y = hub.position[1] * 150 + center_y
                    drone_sprite.target_x = drone_sprite.center_x
                    drone_sprite.target_y = drone_sprite.center_y
                    drone_sprite.simdrone = drone_data
                    
                    self.drone_sprites.append(drone_sprite)

    def get_center(self) -> tuple[int, int]:
        hubs = self.map_fly.hubs

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
        hubs = self.map_fly.hubs
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
            hub_name = arcade.Text(hubs[hub].name, x, y - 5,
                                   arcade.color.BLACK, font_size=8)
            hub_name.draw()
        self.drone_sprites.draw()
        output = f"Total Turns: {self.simulation.turn}"
        arcade.draw_text(output, 10, 20, arcade.color.WHITE, 14)

    def on_update(self, time):
        drones_arrived = True
        center_x, center_y = self.get_center()
        for drone in self.drone_sprites:
            dis_x = drone.target_x - drone.center_x
            dis_y = drone.target_y - drone.center_y
            if abs(dis_x) > 1 or abs(dis_y) > 1:
                drones_arrived = False
                drone.center_x += dis_x * 0.1
                drone.center_y += dis_y * 0.1
            else:
                drone.center_x = drone.target_x
                drone.center_y = drone.target_y
        
        if drones_arrived:
            simulation_still = self.simulation.simulation_turn()
            if simulation_still:
                hubs = self.map_fly.hubs
                for drone in self.drone_sprites:
                    for hub in hubs.values():
                        if drone.simdrone in hub.drones:
                            drone.target_x = hub.position[0] * 150 + center_x
                            drone.target_y = hub.position[1] * 150 + center_y
                            break
                    
            

            
            

if __name__ == "__main__":
    try:
        map_parsing = MapParser("maps/medium/03_priority_puzzle.txt")
        map_parsing.get_main_settings()
        map_fly = Map(map_parsing)

        simulation = Manager(map_fly)
        simulation.initiate_simulation()
        # while simulation.simulation_turn():
        #     pass
        renderer = MapDisplay(1920, 1080, "Fly-in", simulation)
        arcade.run()
        print(simulation.turn)
    except Exception as e:
        print(e)
