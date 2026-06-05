import pygame
from parser import MapParser, Connection

class MapDisplay:
    def __init__(self, config: MapParser):
        self.config = config

    def display_connection(self, surface, connect: Connection, size_x, size_y):
        pos_x_start, pos_y_start = connect.hubs[0].position
        pos_x_end, pos_y_end = connect.hubs[1].position
        pygame.draw.line(surface, "black",
                            (pos_x_start * 50 + size_x,
                             pos_y_start * 50 + size_y),
                            (pos_x_end * 50 + size_x,
                             pos_y_end * 50 + size_y), 15)

    def main_display(self):
        pygame.init()
        size_x = 1280
        size_y = 720
        screen = pygame.display.set_mode((size_x, size_y))
        clock = pygame.time.Clock()

        while True:
            screen.fill("white")
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        
                    pygame.quit()
                    raise SystemExit
            for connect in self.config.connections:
                self.display_connection(screen,
                                        self.config.connections[connect],
                                        size_x / 4, size_y / 4)
                for hub in self.config.hubs:
                    x, y = self.config.hubs[hub].position
                    x = x * 50 + (size_x / 4)
                    y = y * 50 + (size_y / 4)
                    pygame.draw.circle(screen, self.config.hubs[hub].color, (x, y), 35)
            pygame.display.flip()
            clock.tick(60)


if __name__ == "__main__":
    settings = MapParser('config.txt')
    settings.get_main_settings()
    graph = MapDisplay(settings)
    graph.main_display()