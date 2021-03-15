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
                _x = x * MESH_SIZE
                _y = y * MESH_SIZE
                if MAP[y][x] == WALL:
                    pygame.draw.rect(screen, (0, 255, 0),
                                     ((_x, _y), (MESH_SIZE, MESH_SIZE)))
                elif MAP[y][x] == 2:
                    pygame.draw.rect(screen, (255, 0, 0),
                                     ((_x, _y), (MESH_SIZE, MESH_SIZE)))

        for x in range(self.size[0] + 1):
            _x = x * MESH_SIZE
            _y = self.size[1] * MESH_SIZE
            pygame.draw.line(screen, (0, 180, 0), (_x, 0), (_x, _y))

        for y in range(self.size[1] + 1):
            _x = self.size[0] * MESH_SIZE
            _y = y * MESH_SIZE
            pygame.draw.line(screen, (0, 180, 0), (0, _y), (_x, _y))


class Player:
    def __init__(self, pos: list):
        # все на листах дабы можно было делать ссылки для рейкаст камеры
        self.pos = list(pos)
        self.angle = [-18000.0]
        self.radius = [10]

        # скорость, множитель ускорения и множитель замедления
        self.speed = [2.0]
        self.acceleration = [2.0]
        self.deceleration = [0.3]

        # все для хп (ничего пока)

        # тут все для стамины, реген - реген, лимит - [максимум, порог замендления]
        self.stamina = [400.0]
        self.stamina_regen = [4.0]
        self.stamina_limit = [400.0, 80.0]

        # малеха статистики
        self.all_distance = [0.0]

        # это для таймера
        self.tickrate = 0
        self.tickstart = -1

    def draw(self, screen):
        pygame.draw.circle(screen, (180, 0, 0),
                           (round(self.pos[0]), round(self.pos[1])), self.radius[0])

    def moveForward(self, distance: int):
        '''to move forward send a positive argument else negative'''
        x = self.pos[0] + math.cos(math.radians(self.angle[0])) * distance
        y = self.pos[1] + math.sin(math.radians(self.angle[0])) * distance
        if MAP[int(y) // MESH_SIZE][int(x) // MESH_SIZE] == EMPTY:
            self.all_distance[0] += distance
            self.pos[0] = x
            self.pos[1] = y

    def moveSide(self, distance: int):
        '''to move to the right side send a positive argument else negative'''
        x = self.pos[0] + \
            math.cos(math.radians(self.angle[0] + 90.0)) * distance
        y = self.pos[1] + \
            math.sin(math.radians(self.angle[0] + 90.0)) * distance
        if MAP[int(y) // MESH_SIZE][int(x) // MESH_SIZE] == EMPTY:
            self.all_distance[0] += distance
            self.pos[0] = x
            self.pos[1] = y

    def rotation(self, angle: float):
        self.angle[0] -= angle

    def movement(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            speed = self.speed[0]

            # если есть стамина, то можем ускоряться, нет - замедляемся
            if self.stamina[0] > self.stamina_limit[1]:
                if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                    speed *= self.acceleration[0]
            else:
                speed *= self.deceleration[0]

            # стамина тратиться если нажата кнопка шифта
            self.stamina[0] -= self.speed[0] * \
                (1 if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] else 0)

            player.moveForward(speed)

        # в кажом ифе проверяем наличие стамины
        if keys[pygame.K_a]:
            player.moveSide(-self.speed[0] * (self.deceleration[0]
                                              if self.stamina[0] <= self.stamina_limit[1] else 1.0))
        if keys[pygame.K_s]:
            player.moveForward(-self.speed[0] * (self.deceleration[0]
                                                 if self.stamina[0] <= self.stamina_limit[1] else 1.0))
        if keys[pygame.K_d]:
            player.moveSide(+self.speed[0] * (self.deceleration[0]
                                              if self.stamina[0] <= self.stamina_limit[1] else 1.0))

    def stateUpdate(self):
        # тикает раз в 1/10 секунды
        if pygame.time.get_ticks() / 100 >= self.tickstart + 1:
            self.tickstart += 1
            self.tickrate = 0
            # регенит стамину (а должно еще и хп)
            self.stamina[0] = min(
                max(0, self.stamina[0] + self.stamina_regen[0]), self.stamina_limit[0])
        else:
            self.tickrate += 1


class RayCastCamera:
    def __init__(self, player: Player):
        self.pos = player.pos

        self.pl_stamina = player.stamina
        self.pl_stamina_lim = player.stamina_limit

        self.direction = player.angle
        self.cursor_HUD = pygame.image.load("cursor.png")
        self.bar_HUD = pygame.image.load("bar.png")

    def draw(self, screen):
        # меняем поле зрение в зависимости от скорости персонажа
        if self.pl_stamina[0] > self.pl_stamina_lim[1]:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w] and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
                FOV = 120
            else:
                FOV = 90
        else:
            FOV = 70

        # куча параметров, которые нужны для рисования проекции и которые я хз как описать
        self.step = FOV / RESOLUTION
        self.projection = RESOLUTION / (2.0 * math.radians(FOV / 2.0))

        ray = self.direction[0] - FOV / 2  # луч
        limit = LOD ** 2  # максимальная длинна луча

        # небо
        pygame.draw.rect(screen, (203, 241, 245),
                         ((0, 0),
                          (WIDTH, round(HEIGHT / 2))))

        # пол
        pygame.draw.rect(screen, (34, 40, 49),
                         ((0, round(HEIGHT / 2)),
                          (WIDTH, HEIGHT)))

        while ray < self.direction[0] + FOV / 2:
            # проходим по каждому лучу
            ray += self.step

            # это показатели уменьшения/увеличения х/у координат
            normX = (-1 if math.cos(math.radians(ray)) < 0 else 1)
            normY = (-1 if math.sin(math.radians(ray)) < 0 else 1)

            # обрабатываем лучи по х
            x0 = self.pos[0] - self.pos[0] % MESH_SIZE + \
                (MESH_SIZE if normX < 0 else 0)
            y0 = self.pos[1]

            while (x0 - self.pos[0]) ** 2 + (y0 - self.pos[1]) ** 2 < limit:
                # координаты пересечения луча и границ тайлов
                x0 += MESH_SIZE * normX
                y0 = self.pos[1] + (x0 - self.pos[0]) * \
                    math.tan(math.radians(ray))

                try:
                    # если тайл не пустой - то луч рассеивается
                    x = int(x0 / MESH_SIZE) - (1 if normX < 0 else 0)
                    y = int(y0 / MESH_SIZE)
                    if MAP[y][x] != EMPTY:
                        break
                except:
                    break

            # все то же самое, но для лучей по у
            x1 = self.pos[0]
            y1 = self.pos[1] - self.pos[1] % MESH_SIZE + \
                (MESH_SIZE if normY < 0 else 0)

            while (x1 - self.pos[0]) ** 2 + (y1 - self.pos[1]) ** 2 < limit:
                y1 += MESH_SIZE * normY
                x1 = self.pos[0] + (y1 - self.pos[1]) / \
                    math.tan(math.radians(ray))

                try:
                    x = int(x1 / MESH_SIZE)
                    y = int(y1 / MESH_SIZE) - (1 if normY < 0 else 0)
                    if MAP[y][x] != EMPTY:
                        break
                except:
                    break

            # луч может удаться в стену по х и по у, ближайшую точку столкновения отрисовываем
            l1 = (x0 - self.pos[0]) ** 2 + (y0 - self.pos[1]) ** 2
            l2 = (x1 - self.pos[0]) ** 2 + (y1 - self.pos[1]) ** 2
            coord = (x0, y0) if l1 < l2 else (x1, y1)
            dist = (min(l1, l2) ** 0.5) * \
                math.cos(math.radians(self.direction[0] - ray))

            # если луч вышел из области видимости, то пропускаем
            if min(l1, l2) >= limit:
                continue

            # находим высоту и ширину проекций стен на монитор
            h = min(self.projection * TILE /
                    max(dist, 0.0001), round(HEIGHT / 2))
            w = round(
                (ray - self.direction[0] + FOV / 2) / self.step - 1) * (WIDTH / RESOLUTION)

            # немного глубины цветва (с плавным переливом к цвету неба)
            clr = [234, 186, 148]
            clr_del = [31, 65, 97, (LOD - dist) / LOD]
            clr = [clr[0] - int(clr_del[0] * clr_del[3]),
                   clr[1] - int(clr_del[1] * clr_del[3]),
                   clr[2] - int(clr_del[2] * clr_del[3])]

            # отрисовываем луч (он отражен относительно линии горизхонта, потому прорисовывается верхняя и нижняя части)
            pygame.draw.rect(screen, clr,
                             ((w, math.ceil(HEIGHT / 2)),
                              (math.ceil(WIDTH / RESOLUTION), h)))

            pygame.draw.rect(screen, clr,
                             ((w, math.ceil(HEIGHT / 2) - h + 1),
                              (math.ceil(WIDTH / RESOLUTION), h)))

    def drawHUD(self, screen):
        shift = int(WIDTH * 0.05)
        screen.blit(self.cursor_HUD, ((WIDTH - self.cursor_HUD.get_rect()[2]) // 2,
                                      (HEIGHT - self.cursor_HUD.get_rect()[2]) // 2))

        '''health'''
        pygame.draw.rect(screen, (255, 0, 0),
                         ((shift, HEIGHT - shift),
                          (self.bar_HUD.get_rect()[2], self.bar_HUD.get_rect()[3])))
        screen.blit(self.bar_HUD, (shift, 
                                   HEIGHT - shift))

        '''stamina'''
        pygame.draw.rect(screen, (255, 255, 0),
                         ((int(shift), int(HEIGHT - shift + 2 * self.bar_HUD.get_rect()[3])),
                          (int(self.bar_HUD.get_rect()[2] * self.pl_stamina[0] / self.pl_stamina_lim[0]), self.bar_HUD.get_rect()[3])))
        screen.blit(self.bar_HUD, (shift,
                                   HEIGHT - shift + 2 * self.bar_HUD.get_rect()[3]))


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), vsync=True)
    pygame.mouse.set_visible(False)

    clock = pygame.time.Clock()
    tickrate = 0
    tickstart = -1

    field = Field()

    # создаем персонажа в центре карты
    player = Player((field.size[0] * MESH_SIZE // 2,
                     field.size[1] * MESH_SIZE // 2))

    # создаем камеру и привязываем к персонажу(потому все показатели персонажа на листах)
    view = RayCastCamera(player)

    while True:
        clock.tick(FPS_LOCK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            # поворот персонажа
            if event.type == pygame.MOUSEMOTION:
                player.rotation((WIDTH // 2 - event.pos[0]) * SENSITIVITY)
            pygame.mouse.set_pos((WIDTH // 2, HEIGHT // 2))

        # движение персонажа и обновление статов
        player.movement()
        player.stateUpdate()

        # камера и худ
        view.draw(screen)
        view.drawHUD(screen)

        pygame.display.flip()

        # фпс
        if pygame.time.get_ticks() // 1000 != tickstart:
            tickstart = pygame.time.get_ticks() // 1000
            print("\r" + str(tickrate), end='')
            tickrate = 0
        else:
            tickrate += 1
