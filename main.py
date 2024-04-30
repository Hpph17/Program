import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join
pygame.init()

pygame.display.set_caption("The King")

GB_COLOR = (255, 255, 255)
WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 5
ATTACKING = False

window = pygame.display.set_mode((WIDTH, HEIGHT))

def flip(sprites):
    return[pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("Sprites", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites

def get_block(size):
    path = join("Sprites", "Sprites", "Mapa", "Terra.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(55, 32, 35, 35)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("Sprites", "Rei", 17, 32, True)
    ANIMATION_DELAY = 6
    TYPE_JUMP = 5

    def __init__(self, x, y, width, height):
        super().__init__()
        self.sprite = pygame.image.load(".\\Sprites\\Sprites\\Rei\\Rei caying.png")
        self.rect = pygame.Rect(0, 0, 34, 46)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0

    def jump(self):
        self.y_vel = -self.GRAVITY * self.TYPE_JUMP
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0
            self.TYPE_JUMP * 4

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True
        self.hit_count = 0

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "Rei estanding"
        if self.hit:
            sprite_sheet = "Rei recibing d"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "Rei salting"
            elif self.jump_count == 2:
                sprite_sheet = "Rei salting mes"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "Rei caying"
        elif self.x_vel != 0:
            sprite_sheet = "Rei anding"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

def tile(widht, height):
    tile.rect(x, y, widht, height)

def load_map(path, tile):
    f = open(path + ".txt", "r")
    data = f.read()
    f.close()
    data = data.split("\n")
    game_map =  []
    for row in data:
        game_map.append(list(row))
    if data != 0:
        data = tile
    return game_map

game_map = load_map("map", "tile")
print(game_map)

y = 0

for layer in game_map:
    x = 0
    for tile in layer:
        if tile == "1":
            pygame.image.load("Terra 1.png")
        if tile == "2":
            pygame.image.load("Bloc.png")
        if tile == "3":
            pygame.image.load("Plataforma.png")
        if tile == "4":
            pygame.image.load("Reflorma.png")

class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class Attack(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

class Atac(Attack):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "Atac")
        self.Atac = load_sprite_sheets("Sprites", "Atac", width, height)
        self.image = self.Atac["Atac"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.aniamtion_name = "Atac"

    def loop(self):
        sprites = self.Atac[self.aniamtion_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Serp(Object):
    ANIMATION_DELAY = 15

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "Serp")
        self.Serp = load_sprite_sheets("Sprites", "Serp", width, height)
        self.image = self.Serp["Serp"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.aniamtion_name = "Serp"

    def loop(self):
        sprites = self.Serp[self.aniamtion_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

def get_background(name):
    image = pygame.image.load(join("Sprites", "Sprites", "Mapa", name))
    _, _, width, height = image.get_rect()
    trees = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            trees.append(pos)

    return trees, image

def draw(window, background, bg_image, player, objects, offset_x, floor, Atac, game_map):
    for tree in background:
        window.blit(bg_image, tree)

    for obj in objects:
        obj.draw(window, offset_x)
        # rect = pygame.Rect((obj.rect.left - offset_x, obj.rect.top), obj.rect.size)
        # pygame.draw.rect(window, (0, 0, 0), rect)

    Atac.draw(window, offset_x)

    player.draw(window, offset_x)

    pygame.display.update()
    print(game_map)
    game_map.draw

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if obj.rect.colliderect(player.rect):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects

def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object

def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_a] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_d] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]
    for obj in to_check:
        if obj and obj.name == "Serp":
            player.make_hit()

def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Fons.png")

    block_size = 96

    player = Player(100, 100, 50, 50)
    serp = Serp(400, HEIGHT - block_size, 18, 14)
    floor = [Block(i * block_size, HEIGHT - block_size + 40, block_size * 2)
             for i in range(-WIDTH // block_size, (WIDTH * 4) // block_size)]
    objects = [*floor, Block(0, HEIGHT - block_size * 2, 70),
               Block(block_size * 3, HEIGHT - block_size * 4, 70), serp]
    Atac = Attack(100, 100, 50, 50)

    offset_x = 0
    scroll_area_width = 200
    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

                global PLAYER_VEL

                if event.key == pygame.K_UP:
                    player.GRAVITY = 5
                    PLAYER_VEL = 10

                if event.key == pygame.K_LEFT:
                    player.GRAVITY = 2.5
                    PLAYER_VEL = 7

                if event.key == pygame.K_DOWN:
                    player.GRAVITY = 0.5
                    PLAYER_VEL = 2.5

                global ATTACKING

                if event.key == pygame.K_RIGHT:
                    ATTACKING = True

        player.loop(FPS)
        serp.loop()
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x, floor, Atac, game_map)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)