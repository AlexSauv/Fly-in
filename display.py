import pygame
from parser import MapParser, Connection, Hub

class MapDisplay:
    def __init__(self, config: MapParser, width, height):
        self.config = config
        self.width = width
        self.height = height
        self.scale = 60
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.calculate_center()

    def calculate_center(self) -> None:
        if not self.config.hubs:
            raise ValueError("[RENDER] There is no hubs established.")
        x_hubs = [hub.position[0] for hub in self.config.hubs.values()]
        y_hubs = [hub.position[1] for hub in self.config.hubs.values()]

        min_x, max_x = min(x_hubs), max(x_hubs)
        min_y, max_y = min(y_hubs), max(y_hubs)

        map_width = max(max_x - min_x, 1)
        map_height = max(max_y - min_y, 1)
        
        padding = 60
        scale_x = (self.width - 2 * padding) / map_width
        scale_y = (self.height - 2 * padding) / map_height

        self.scale = min(scale_x, scale_y)
        mid_x = (min_x + max_x) / 2
        mid_y = (min_y + max_y) / 2

        self.offset_x = (self.width / 2) - (mid_x * self.scale)
        self.offset_y = (self.height / 2) - (mid_y * self.scale)

    def get_map_size(self, pos):
        pos_x = pos[0]
        pos_y = pos[1]

        map_x = int(pos_x * self.scale + self.offset_x)
        map_y = int(pos_y * self.scale + self.offset_y)
        return (map_x, map_y)

    def display_connection(self, surface, connect: Connection):        
        start_line = self.get_map_size(connect.hubs[0].position)
        end_line = self.get_map_size(connect.hubs[1].position)
        pygame.draw.line(surface, (245, 245, 245), start_line, end_line, 6)
    
    def display_hub(self, surface: pygame.Surface, hub: Hub, 
                    font: pygame.font.Font):
        cx, cy = self.get_map_size(hub.position)
        try:
            color = pygame.Color(hub.color)
        except ValueError:
            color = pygame.Color("blue")
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 24, 1)
        pygame.draw.circle(surface, color, (cx, cy), 22)
        # name_surf = font.render(hub.name, True, (255, 255, 255))
        # total_drones = font.render(f"{hub.name} drones: {hub.drones}", True, (255, 255, 255))
        # surface.blit(name_surf, (cx - name_surf.get_width() // 2, cy - 50))
        # surface.blit(total_drones, (50, self.height // 2 + gap))
        # if hub.drones > 0:
        #     surface.blit(drone_img, (cx, cy), )

    def main_display(self):
        drone = pygame.image.load("drone_one.png")
        pygame.init()
        pygame.font.init()
        font_small = pygame.font.SysFont("Arial", 16, bold=True)
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Fly_in - by Alsauvan")
        clock = pygame.time.Clock()

        while True:
            screen.fill((15, 23, 42))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

            for connect in self.config.connections.values():
                self.display_connection(screen, connect)

            for hub in self.config.hubs.values():
                self.display_hub(screen, hub, font_small)
                    
            pygame.display.flip()
            clock.tick(60)


if __name__ == "__main__":
    settings = MapParser('maps/easy/02_simple_fork.txt')
    settings.get_main_settings()
    graph = MapDisplay(settings, 1244, 900)
    graph.main_display()