import pygame
import copy
import math
from pygame import cursors

from pygame.constants import BUTTON_X1

from config import *


class Field:
    def __init__(self):
        self.size = [len(MAP[0]), len(MAP)]

    def draw(self, screen):
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                _x = x * MESH_SIZE  # - 1
                _y = y * MESH_SIZE  # - 1
                if MAP[y][x] == WALL:
                    pygame.draw.rect(screen, (0, 255, 0),
                                     ((_x, _y), (MESH_SIZE, MESH_SIZE)))
                elif MAP[y][x] == 2:
                    pygame.draw.rect(screen, (255, 0, 0),
                                     ((_x, _y), (MESH_SIZE, MESH_SIZE)))

        for x in range(self.size[0] + 1):
            _x = x * MESH_SIZE  # - 1
            _y = self.size[1] * MESH_SIZE  # - 1
            pygame.draw.line(screen, (0, 180, 0), (_x, 0), (_x, _y))

        for y in range(self.size[1] + 1):
            _x = self.size[0] * MESH_SIZE  # - 1
            _y = y * MESH_SIZE  # - 1
            pygame.draw.line(screen, (0, 180, 0), (0, _y), (_x, _y))


class Player:
    def __init__(self):
        self.pos = [0, 0]
        self.angle = [-18000.0]
        self.radius = [10]

    def draw(self, screen):
        pygame.draw.circle(screen, (180, 0, 0),
                           (round(self.pos[0]), round(self.pos[1])), self.radius[0])

    def moveForward(self, distance: int):
        '''to move forward send a positive argument else negative'''
        x = self.pos[0] + math.cos(math.radians(self.angle[0])) * distance
        y = self.pos[1] + math.sin(math.radians(self.angle[0])) * distance
        if MAP[int(y) // MESH_SIZE][int(x) // MESH_SIZE] == EMPTY:
            self.pos[0] = int(x)
            self.pos[1] = int(y)

    def moveSide(self, distance: int):
        '''to move to the right side send a positive argument else negative'''
        x = self.pos[0] + \
            math.cos(math.radians(self.angle[0] + 90.0)) * distance
        y = self.pos[1] + \
            math.sin(math.radians(self.angle[0] + 90.0)) * distance
        if MAP[int(y) // MESH_SIZE][int(x) // MESH_SIZE] == EMPTY:
            self.pos[0] = int(x)
            self.pos[1] = int(y)

    def rotation(self, angle: float):
        self.angle[0] -= angle


class RayCastCamera:
    def __init__(self, player: Player):
        self.pos = player.pos
        self.direction = player.angle

        self.step = FOV / RESOLUTION
        self.projection = RESOLUTION / (2.0 * math.radians(FOV / 2.0))

        self.cursor = pygame.image.load("cursor.png")

    def draw(self, screen):
        ray = self.direction[0] - FOV / 2
        limit = LOD ** 2

        pygame.draw.rect(screen, (203, 241, 245),
                         ((0, 0),
                          (WIDTH, round(HEIGHT / 2))))

        pygame.draw.rect(screen, (34, 40, 49),
                         ((0, round(HEIGHT / 2)),
                          (WIDTH, HEIGHT)))

        while ray < self.direction[0] + FOV / 2:
            ray += self.step

            normX = (-1 if math.cos(math.radians(ray)) < 0 else 1)
            normY = (-1 if math.sin(math.radians(ray)) < 0 else 1)

            x0 = self.pos[0] - self.pos[0] % MESH_SIZE + \
                (MESH_SIZE if normX < 0 else 0)
            y0 = self.pos[1]

            while (x0 - self.pos[0]) ** 2 + (y0 - self.pos[1]) ** 2 < limit:
                x0 += MESH_SIZE * normX
                y0 = self.pos[1] + (x0 - self.pos[0]) * \
                    math.tan(math.radians(ray))

                x = int(x0 / MESH_SIZE) - (1 if normX < 0 else 0)
                y = int(y0 / MESH_SIZE)

                try:
                    if MAP[y][x] != EMPTY:
                        break
                except:
                    break

            x1 = self.pos[0]
            y1 = self.pos[1] - self.pos[1] % MESH_SIZE + \
                (MESH_SIZE if normY < 0 else 0)

            while (x1 - self.pos[0]) ** 2 + (y1 - self.pos[1]) ** 2 < limit:
                y1 += MESH_SIZE * normY
                x1 = self.pos[0] + (y1 - self.pos[1]) / \
                    math.tan(math.radians(ray))

                x = int(x1 / MESH_SIZE)
                y = int(y1 / MESH_SIZE) - (1 if normY < 0 else 0)

                try:
                    if MAP[y][x] != EMPTY:
                        break
                except:
                    break

            l1 = (x0 - self.pos[0]) ** 2 + (y0 - self.pos[1]) ** 2
            l2 = (x1 - self.pos[0]) ** 2 + (y1 - self.pos[1]) ** 2
            coord = (x0, y0) if l1 < l2 else (x1, y1)
            dist = (min(l1, l2) ** 0.5) * \
                math.cos(math.radians(self.direction[0] - ray))

            if min(l1, l2) ** 0.5 >= LOD:
                continue

            h = min(self.projection * TILE /
                    max(dist, 0.0001), round(HEIGHT / 2))
            w = (
                int(((ray - self.direction[0] + FOV / 2) / self.step)) / RESOLUTION) * WIDTH

            clr = [234, 186, 148]
            clr_del = [31, 65, 97, (LOD - dist) / LOD]
            clr = [clr[0] - int(clr_del[0] * clr_del[3]),
                   clr[1] - int(clr_del[1] * clr_del[3]),
                   clr[2] - int(clr_del[2] * clr_del[3])]

            pygame.draw.rect(screen, clr,
                             ((w, math.ceil(HEIGHT / 2)),
                              (math.ceil(WIDTH / RESOLUTION), h)))

            pygame.draw.rect(screen, clr,
                             ((w, math.ceil(HEIGHT / 2) - h + 1),
                              (math.ceil(WIDTH / RESOLUTION), h)))

        screen.blit(self.cursor, (WIDTH // 2 - 7, HEIGHT // 2 - 7))


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), vsync=True)
    pygame.mouse.set_visible(False)

    clock = pygame.time.Clock()
    tickrate = 0
    tickstart = -1

    field = Field()

    player = Player()
    player.pos = [(field.size[0] * MESH_SIZE // 2),
                  (field.size[1] * MESH_SIZE // 2)]

    view = RayCastCamera(player)

    while True:
        clock.tick(FPS_LOCK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEMOTION:
                player.rotation((WIDTH // 2 - event.pos[0]) * SENSITIVITY)

            pygame.mouse.set_pos((WIDTH // 2, HEIGHT // 2))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            player.moveForward(+2)
        if keys[pygame.K_a]:
            player.moveSide(-2)
        if keys[pygame.K_s]:
            player.moveForward(-2)
        if keys[pygame.K_d]:
            player.moveSide(+2)

        view.draw(screen)
        # field.draw(screen)
        # player.draw(screen)
        pygame.display.flip()

        if pygame.time.get_ticks() // 1000 != tickstart:
            tickstart = pygame.time.get_ticks() // 1000
            print("\r" + str(tickrate), end='')
            tickrate = 0
        else:
            tickrate += 1
