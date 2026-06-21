import sys
import subprocess
import arcade
from algorithm import Map
from parser import MapParser
from simulator import Manager


class MapDisplay(arcade.Window):
    def __init__(self, width, height, title, maps: list[str]):
        super().__init__(width, height, title)
        self.width = width
        self.height = height
        self.maps = maps
        self.maps_index = 0

        self.background = arcade.load_texture("background_img.jpg")
        self.drone_txt = arcade.load_texture("drone_img.png")
        self.drone_sprites = arcade.SpriteList()
        self.camera = arcade.Camera2D()
        self.load_map_simulation()

    def load_map_simulation(self):
        current_path = self.maps[self.maps_index]
        map_parsing = MapParser(current_path)
        map_parsing.get_main_settings()
        self.curr_map = Map(map_parsing)

        self.simu = Manager(self.curr_map)
        self.simu.initiate_simulation()
        self.zoom_level = 1.0
        self.simturn = None
        self.simturn_finished = False
        self.drone_move = False
        self.auto = False

        self.set_drone()
        self.update_camera()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.RIGHT:
            if self.drone_move or self.auto:
                return
            self.simturn = self.simu.simulation_turn()
            self.drone_move = True
        if key == arcade.key.N:
            self.maps_index = (self.maps_index + 1) % len(self.maps)
            self.load_map_simulation()
        if key == arcade.key.P:
            self.maps_index = (self.maps_index - 1) % len(self.maps)
            self.load_map_simulation()
        if key == arcade.key.A:
            self.auto = not self.auto
        if key == arcade.key.ESCAPE:
            arcade.exit()

    def update_camera(self):
        self.camera.position = (self.width // 2, self.height // 2)
        self.camera.zoom = 1.0 / self.zoom_level

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if scroll_y > 0:
            self.zoom_level -= 0.5
        else:
            self.zoom_level += 0.5

        self.zoom_level = max(0.2, min(self.zoom_level, 3.0))
        self.update_camera()

    def set_drone(self) -> None:
        center_x, center_y = self.get_center()
        self.drone_sprites.clear()
        hubs = self.curr_map.hubs
        for hub in hubs.values():
            if hub.drones:
                for drone_data in hub.drones:
                    drone_sprt = arcade.SpriteCircle(12,
                                                     arcade.color.WHITE_SMOKE)
                    drone_sprt = arcade.Sprite(self.drone_txt, scale=0.09)
                    drone_sprt.color = arcade.color.WHITE_SMOKE
                    drone_sprt.center_x = hub.position[0] * 150 + center_x
                    drone_sprt.center_y = hub.position[1] * 150 + center_y
                    drone_sprt.target_x = drone_sprt.center_x
                    drone_sprt.target_y = drone_sprt.center_y
                    drone_sprt.s_drone = drone_data

                    self.drone_sprites.append(drone_sprt)

    def get_center(self) -> tuple[int, int]:
        hubs = self.curr_map.hubs

        min_x = min([hubs[hub].position[0] for hub in hubs])
        min_y = min([hubs[hub].position[1] for hub in hubs])
        max_x = max([hubs[hub].position[0] for hub in hubs])
        max_y = max([hubs[hub].position[1] for hub in hubs])

        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2

        offset_x = (self.width / 2) - (center_x * 150)
        offset_y = (self.height / 2) - (center_y * 150)

        return offset_x, offset_y
    
    def sum_keyboard(self):
        arcade.Text("PRESS YOUR KEYS:",
                    30,
                    110,
                    arcade.color.WHITE,
                    12).draw()
        arcade.Text("P / N -> Previous Map / Next Map",
                    30,
                    80,
                    arcade.color.WHITE,
                    12).draw()
        arcade.Text("A -> Auto mode",
                    30,
                    60,
                    arcade.color.WHITE,
                    12).draw()
        arcade.Text("Right -> Next turn (on auto disabled)",
                    30,
                    40,
                    arcade.color.WHITE,
                    12).draw()

    def on_draw(self):
        self.clear()
        self.camera.use()
        arcade.draw_texture_rect(
            self.background,
            arcade.LBWH(0, 0,
                        self.width,
                        self.height))
        self.sum_keyboard()
        hubs = self.curr_map.hubs
        connections = self.curr_map.connections

        center_x, center_y = self.get_center()
        for connection in connections:
            hub_start = connections[connection].hubs[0]
            hub_end = connections[connection].hubs[1]

            start_x = hub_start.position[0] * 150 + center_x
            start_y = hub_start.position[1] * 150 + center_y

            end_x = hub_end.position[0] * 150 + center_x
            end_y = hub_end.position[1] * 150 + center_y

            mid_x = (start_x + end_x) / 2
            mid_y = (start_y + end_y) / 2

            drones_co = len(connections[connection].drones)
            total_drones = (f"{drones_co}/"
                            f"{connections[connection].max_link_capacity}")
            arcade.Text(total_drones,
                        mid_x - 5,
                        mid_y + 20,
                        arcade.color.WHITE,
                        12).draw()
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
            arcade.Text(hubs[hub].name,
                        x,
                        y - 50,
                        arcade.color.WHITE,
                        font_size=10,
                        anchor_x='center').draw()
            filled = f"{len(hubs[hub].drones)}/{hubs[hub].max_drones}"
            arcade.Text(filled,
                        x,
                        y,
                        arcade.color.WHITE,
                        12,
                        anchor_x='center',
                        anchor_y='center').draw()

        self.drone_sprites.draw()
        for drone_num in self.drone_sprites:
            num = drone_num.s_drone

            n_drone_x = drone_num.center_x
            n_drone_y = drone_num.center_y

            arcade.Text(
                num,
                n_drone_x,
                n_drone_y + 3,
                arcade.color.WHITE,
                font_size=6,
                bold=True,
                anchor_x='center',
                anchor_y='center').draw()

        if self.simturn_finished:
            self.clear()
            arcade.camera.Camera2D().use()
            result = ("FINISHED ! All drones arrived"
                      f" in {self.simu.turn} turns")
            arcade.Text(result,
                        self.width // 2,
                        self.height // 2,
                        arcade.color.WHITE,
                        24,
                        anchor_x='center',
                        anchor_y='center').draw()
            return

    def on_update(self, delta_time):
        drones_arrived = True
        total_drones = len(self.drone_sprites)
        goal_drones = len(self.curr_map.end_hub.drones)
        center_x, center_y = self.get_center()

        for drone in self.drone_sprites:
            dis_x = drone.target_x - drone.center_x
            dis_y = drone.target_y - drone.center_y

            if abs(dis_x) > 1 or abs(dis_y) > 1:
                drones_arrived = False
                drone.center_x += dis_x * 0.3
                drone.center_y += dis_y * 0.3
            else:
                drone.center_x = drone.target_x
                drone.center_y = drone.target_y

        if drones_arrived:
            self.drone_move = False
            if self.auto and not self.simturn_finished:
                self.simturn = self.simu.simulation_turn()
                self.drone_move = True

            if self.simturn:
                hubs = self.curr_map.hubs
                for drone in self.drone_sprites:
                    in_hub = False
                    for hub in hubs.values():
                        if drone.s_drone in hub.drones:
                            in_hub = True
                            drone.target_x = hub.position[0] * 150 + center_x
                            drone.target_y = hub.position[1] * 150 + center_y
                            break
                    if not in_hub:
                        connections = self.curr_map.connections
                        for connect in connections.values():
                            if drone.s_drone in connect.drones:
                                hub_start = connect.hubs[0]
                                hub_end = connect.hubs[1]

                                mid_x = (hub_start.position[0] +
                                         hub_end.position[0]) / 2
                                mid_y = (hub_start.position[1] +
                                         hub_end.position[1]) / 2

                                drone.target_x = mid_x * 150 + center_x
                                drone.target_y = mid_y * 150 + center_y
                                break
                self.simturn = None
                self.drone_move = True
            elif total_drones == goal_drones:
                self.simturn_finished = True


if __name__ == "__main__":
    try:
        maps = ["maps/easy/01_linear_path.txt",
                "maps/easy/02_simple_fork.txt",
                "maps/easy/03_basic_capacity.txt",
                "maps/medium/01_dead_end_trap.txt",
                "maps/medium/02_circular_loop.txt",
                "maps/medium/03_priority_puzzle.txt",
                "maps/hard/01_maze_nightmare.txt",
                "maps/hard/02_capacity_hell.txt",
                "maps/hard/03_ultimate_challenge.txt",
                "maps/challenger/01_the_impossible_dream.txt"
                ]
        renderer = MapDisplay(2400, 1200, "Fly-in", maps)
        arcade.run()
    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        subprocess.run('clear', shell=True)
        print("Fly in simulation closed.")
        sys.exit(0)
