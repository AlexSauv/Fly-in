import arcade
from typing import Any
from map_config import MapConfig, ZoneType
# from parser import FileParser
from simulator import Manager


class MapDisplay(arcade.Window):
    """
        Class for rendering output and programming
        visualisation of drones steps through the map
    """
    def __init__(self, width: int, height: int,
                 title: str, map: str):
        super().__init__(width, height, title)
        self.width = width
        self.height = height
        self.map = map
        self.first_map_load = False
        self.maps = ["maps/easy/01_linear_path.txt",
                     "maps/easy/02_simple_fork.txt",
                     "maps/easy/03_basic_capacity.txt",
                     "maps/medium/01_dead_end_trap.txt",
                     "maps/medium/02_circular_loop.txt",
                     "maps/medium/03_priority_puzzle.txt",
                     "maps/hard/01_maze_nightmare.txt",
                     "maps/hard/02_capacity_hell.txt",
                     "maps/hard/03_ultimate_challenge.txt",
                     "maps/challenger/01_the_impossible_dream.txt"]
        self.maps_index = 0

        self.background = arcade.load_texture("src/background_img.jpg")
        self.drone_txt = arcade.load_texture("src/drone_img.png")
        self.drone_sprites: arcade.SpriteList[Any] = arcade.SpriteList()
        self.hub_colors_cache: dict[str, Any] = {}
        self.camera = arcade.Camera2D()

        self.sum_text_list: list[arcade.Text] = []
        self.hub_text_objects: dict[str, dict[str, arcade.Text]] = {}
        self.connection_text_objects: dict[str, arcade.Text] = {}
        self.map_title_text: arcade.Text | None = None

        self.setup_sum_text()
        self.load_map_simulation()

    def load_map_simulation(self) -> None:
        """
            This function handle entrees map
            files and load simulation data
        """
        if not self.first_map_load:
            found = False
            for map in self.maps:
                if map.endswith(self.map):
                    self.maps_index = self.maps.index(map)
                    self.first_map_load = True
                    found = True
            if not found:
                raise ValueError(f"[MAP] The {self.map} map is not found")

        current_path = self.maps[self.maps_index]
        # map_parsing = FileParser(current_path)
        self.curr_map = MapConfig(current_path)
        self.curr_map.generate_map()

        self.simu = Manager(self.curr_map)
        self.simu.initiate_simulation()
        if self.curr_map.map_name == "01_the_impossible_dream":
            self.mltp = 100
        else:
            self.mltp = 150

        self.simturn: bool = False
        self.simturn_finished = False
        self.drone_move = False
        self.auto = False

        self.hub_colors_cache.clear()
        for hub_id, hub in self.curr_map.hubs.items():
            color_str = hub.color.upper()
            if color_str.startswith("#"):
                hex_val = color_str.lstrip("#")
                self.hub_colors_cache[hub_id] = (
                    int(hex_val[0:2], 16),
                    int(hex_val[2:4], 16),
                    int(hex_val[4:6], 16)
                )
            elif hasattr(arcade.color, color_str):
                self.hub_colors_cache[hub_id] = getattr(arcade.color,
                                                        color_str)
            else:
                raise ValueError(f"[DISPLAY] {color_str} color not found")

        self.map_title_text = arcade.Text(
            self.curr_map.map_name, self.width // 2, self.height - 50,
            arcade.color.WHITE, 20, anchor_x='center'
        )
        self.hub_text_objects.clear()
        self.connection_text_objects.clear()

        self.set_drone()
        self.pre_drone_pos()

        self.update_text_cache()

    def pre_drone_pos(self) -> None:
        """
        pre calculate coordinate (x, y) for each drone during each turns
        """
        self.drone_pos_by_turn = {}
        center_x, center_y = self.get_center()
        for drone_id, path in self.simu.drones_path.items():
            first_hub_name, first_turn = path[0]
            first_hub = self.curr_map.hubs[first_hub_name]
            start_x = first_hub.position[0] * self.mltp + center_x
            start_y = first_hub.position[1] * self.mltp + center_y
            self.drone_pos_by_turn[(drone_id, first_turn)] = (start_x, start_y)

            for i in range(len(path) - 1):
                curr_hub_name, curr_turn = path[i]
                next_hub_name, next_turn = path[i + 1]

                curr_hub = self.curr_map.hubs[curr_hub_name]
                next_hub = self.curr_map.hubs[next_hub_name]

                x_curr = curr_hub.position[0] * self.mltp + center_x
                y_curr = curr_hub.position[1] * self.mltp + center_y
                x_next = next_hub.position[0] * self.mltp + center_x
                y_next = next_hub.position[1] * self.mltp + center_y
                if next_turn - curr_turn > 1:
                    for missing_turn in range(curr_turn + 1, next_turn):
                        inter_x = (x_curr + x_next) // 2
                        inter_y = (y_curr + y_next) // 2
                        self.drone_pos_by_turn[
                            (drone_id, missing_turn)] = (inter_x, inter_y)
                self.drone_pos_by_turn[
                        (drone_id, next_turn)] = (x_next, y_next)

    def update_text_cache(self) -> None:
        """create and update text for each connexion and hub """
        hubs = self.curr_map.hubs
        connections = self.curr_map.connections
        center_x, center_y = self.get_center()
        ratio = max(0.4, min(self.mltp / 150.0, 1.0))
        font_size_connections = max(8, int(12 * ratio))
        font_size_hubs = max(8, int(12 * ratio))

        for link_name, connection in connections.items():
            hub_start = connection.hubs[0]
            hub_end = connection.hubs[1]
            mid_x = ((hub_start.position[0] +
                      hub_end.position[0]) * self.mltp / 2) + center_x
            mid_y = ((hub_start.position[1] +
                      hub_end.position[1]) * self.mltp / 2) + center_y

            total_drones = f"{len(connection.drones)
                              }/{connection.max_link_capacity}"

            if link_name not in self.connection_text_objects:
                self.connection_text_objects[link_name] = arcade.Text(
                    total_drones, mid_x, mid_y + (12 * ratio),
                    arcade.color.RED,
                    font_size=font_size_connections,
                    anchor_x='center')
            else:
                self.connection_text_objects[link_name].text = total_drones

        for hub_id, hub in hubs.items():
            x = hub.position[0] * self.mltp + center_x
            y = hub.position[1] * self.mltp + center_y
            filled = f"{len(hub.drones)}/{hub.max_drones}"

            if hub_id not in self.hub_text_objects:
                self.hub_text_objects[hub_id] = {
                    "name": arcade.Text(hub.name, x, y - 50,
                                        arcade.color.WHITE,
                                        font_size=font_size_hubs,
                                        anchor_x='center'),
                    "capacity": arcade.Text(filled,
                                            x,
                                            y,
                                            arcade.color.WHITE,
                                            12,
                                            anchor_x='center',
                                            anchor_y='center')
                }
            else:
                self.hub_text_objects[hub_id]["capacity"].text = filled

    def on_key_press(self, key: int, _: int) -> None:
        """
            Program even for key pressing: changing maps,
            auto drones fly throught the map, execute turns,
            exit programs
        """
        if key == arcade.key.RIGHT:
            if self.drone_move or self.auto:
                return
            self.simturn = self.simu.simulation_turn()
            self.drone_move = True
            if self.simturn_finished:
                self.maps_index = (self.maps_index + 1) % len(self.maps)
                self.load_map_simulation()
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

    def set_drone(self) -> None:
        """ this function set drones visual representation"""
        center_x, center_y = self.get_center()
        self.drone_sprites.clear()
        hubs = self.curr_map.hubs
        for hub in hubs.values():
            if hub.drones:
                for drone_data in hub.drones:
                    drone_sprt: Any = arcade.SpriteCircle(12,
                                                          arcade.color.PURPLE)
                    drone_sprt = arcade.Sprite(self.drone_txt, scale=0.09)
                    drone_sprt.color = arcade.color.WHITE_SMOKE
                    drone_sprt.center_x = (hub.position[0] *
                                           self.mltp + center_x)
                    drone_sprt.center_y = (hub.position[1] *
                                           self.mltp + center_y)
                    drone_sprt.target_x = drone_sprt.center_x
                    drone_sprt.target_y = drone_sprt.center_y
                    drone_sprt.id_drone = drone_data

                    self.drone_sprites.append(drone_sprt)

    def get_center(self) -> tuple[float, float]:
        """
            this function is for calculate
            center of the window for an element
        """
        hubs = self.curr_map.hubs

        min_x = min([hubs[hub].position[0] for hub in hubs])
        min_y = min([hubs[hub].position[1] for hub in hubs])
        max_x = max([hubs[hub].position[0] for hub in hubs])
        max_y = max([hubs[hub].position[1] for hub in hubs])

        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2

        offset_x = (self.width / 2) - (center_x * self.mltp)
        offset_y = (self.height / 2) - (center_y * self.mltp)

        return offset_x, offset_y

    def setup_sum_text(self) -> None:
        """
            This function is used to pre-set
            summary of key text
        """
        self.sum_text_list = [
            arcade.Text("PRESS YOUR KEYS:", 30, 150, arcade.color.WHITE, 12),
            arcade.Text("[KEY] ESC        -> Quit the program", 30, 120,
                        arcade.color.WHITE, 12),
            arcade.Text("[KEY] P            -> Previous Map", 30, 100,
                        arcade.color.WHITE, 12),
            arcade.Text("[KEY] N           -> Next Map", 30, 80,
                        arcade.color.WHITE, 12),
            arcade.Text("[KEY] A           -> Auto mode (on/off)", 30, 60,
                        arcade.color.WHITE, 12),
            arcade.Text("[KEY] RIGHT   -> Next turn (with auto disabled)",
                        30, 40, arcade.color.WHITE, 12),
            arcade.Text("RING COLOR ZONE SUMMARY:", self.width - 430, 150,
                        arcade.color.WHITE, 12),
            arcade.Text("[COLOR] RED                -> BLOCKED ZONE",
                        self.width - 430, 60,
                        arcade.color.WHITE, 12),
            arcade.Text("[COLOR] GREEN            -> PRIORITY",
                        self.width - 430, 100,
                        arcade.color.WHITE, 12),
            arcade.Text("[COLOR] WHITE             -> NORMAL",
                        self.width - 430, 120,
                        arcade.color.WHITE, 12),
            arcade.Text("[COLOR] ORANGE         -> RESTRICTED",
                        self.width - 430, 80,
                        arcade.color.WHITE, 12)
                        ]

    def on_draw(self) -> None:
        """
            This function is for main visualisation
            of map: hubs, connection, capacity
        """
        self.clear()
        self.camera.use()
        arcade.draw_texture_rect(
            self.background,
            arcade.LBWH(0, 0,
                        self.width,
                        self.height))

        connections = self.curr_map.connections
        center_x, center_y = self.get_center()

        ratio = max(0.4, min(self.mltp / 150.0, 1.0))

        line_width = max(1, int(3 * ratio))
        hub_radius = int(35 * ratio)
        hub_radius_zone = int(38 * ratio)
        hubs = self.curr_map.hubs

        for text_obj in self.sum_text_list:
            text_obj.draw()

        for link_name, connection in connections.items():
            hub_start = connection.hubs[0]
            hub_end = connection.hubs[1]

            start_x = hub_start.position[0] * self.mltp + center_x
            start_y = hub_start.position[1] * self.mltp + center_y

            end_x = hub_end.position[0] * self.mltp + center_x
            end_y = hub_end.position[1] * self.mltp + center_y

            arcade.draw_line(start_x, start_y, end_x, end_y,
                             arcade.color.WHITE, line_width)
            if link_name in self.connection_text_objects:
                self.connection_text_objects[link_name].draw()

        for hub in hubs:
            hub_id = hubs[hub].name
            color_rgb = self.hub_colors_cache[hub_id]
            x = hubs[hub].position[0] * self.mltp + center_x
            y = hubs[hub].position[1] * self.mltp + center_y
            color_rgb = self.hub_colors_cache[hub_id]
            if hubs[hub].zone_type == ZoneType.NORMAL:
                arcade.draw_circle_filled(x, y, hub_radius_zone,
                                          arcade.color.WHITE)
            elif hubs[hub].zone_type == ZoneType.PRIORITY:
                arcade.draw_circle_filled(x, y, hub_radius_zone,
                                          arcade.color.GREEN)
            elif hubs[hub].zone_type == ZoneType.RESTRICTED:
                arcade.draw_circle_filled(x, y, hub_radius_zone,
                                          arcade.color.ORANGE)
            else:
                arcade.draw_circle_filled(x, y, hub_radius_zone,
                                          arcade.color.RED)
            arcade.draw_circle_filled(x, y, hub_radius, color_rgb)

            if hub_id in self.hub_text_objects:
                self.hub_text_objects[hub_id]["name"].draw()
                self.hub_text_objects[hub_id]["capacity"].draw()

        self.drone_sprites.draw()
        for drone_num in self.drone_sprites:
            num = str(drone_num.id_drone)

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
            arcade.camera.Camera2D().use()
            result = ("FINISHED ! Total turns :"
                      f" {self.simu.turn}")
            arcade.Text(result,
                        self.width // 2,
                        self.height - 200,
                        arcade.color.WHITE,
                        24,
                        anchor_x='center',
                        anchor_y='center').draw()
            return

    def on_update(self, delta_time: float) -> None:
        """ This function update each new event... """
        assert self.curr_map.end_hub is not None

        total_drones = len(self.drone_sprites)
        goal_drones = len(self.curr_map.end_hub.drones)

        if self.simturn:
            curr_turn = self.simu.turn
            for sprite in self.drone_sprites:
                drone_id = sprite.id_drone
                pos = self.drone_pos_by_turn.get((drone_id, curr_turn))

                if pos:
                    sprite.target_x, sprite.target_y = pos
            self.update_text_cache()

            self.simturn = False
            self.drone_move = True

        moving = False
        if self.drone_move:
            for sprite in self.drone_sprites:
                dx = sprite.target_x - sprite.center_x
                dy = sprite.target_y - sprite.center_y

                if abs(dx) > 1 or abs(dy) > 1:
                    sprite.center_x += dx * 0.35
                    sprite.center_y += dy * 0.35
                    moving = True
                else:
                    sprite.center_x = sprite.target_x
                    sprite.center_y = sprite.target_y

        if not moving and self.drone_move:
            self.drone_move = False

            if total_drones == goal_drones:
                if not self.simturn_finished:
                    self.simu.generate_output_file()
                    self.simturn_finished = True
        if self.auto and not self.simturn_finished and not self.drone_move:
            self.simturn = self.simu.simulation_turn()
