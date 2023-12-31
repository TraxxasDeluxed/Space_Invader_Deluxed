import pygame
import os
import time

import random

pygame.font.init()

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invader Deluxed")

# Load images
RED_SPACE_player = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_player = pygame.image.load(
    os.path.join("assets", "pixel_ship_green_small.png")
)
BLUE_SPACE_player = pygame.image.load(
    os.path.join("assets", "pixel_ship_blue_small.png")
)

# Player image
YELLOW_SPACE_player = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Background image game
BG = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT)
)


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 20

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.player_img = None
        self.laser_img = None
        self.laser = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.laser:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.laser:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.laser.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.laser.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.laser.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_player
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.laser:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.laser.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.laser:
                            self.laser.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(
            window,
            (255, 0, 0),
            (
                self.x,
                self.y + self.ship_img.get_height() + 10,
                self.ship_img.get_width(),
                10,
            ),
        )
        pygame.draw.rect(
            window,
            (0, 255, 0),
            (
                self.x,
                self.y + self.ship_img.get_height() + 10,
                self.ship_img.get_width() * (self.health / self.max_health),
                10,
            ),
        )


class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_SPACE_player, RED_LASER),
        "green": (GREEN_SPACE_player, GREEN_LASER),
        "blue": (BLUE_SPACE_player, BLUE_LASER),
    }
    horizontal_velocity = 0
    vertical_velocity = 0

    def __init__(self, x, y, color, health=100):  # "red","green", "blue"
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.color = color
        if self.color == "green":
            self.horizontal_velocity = 0.5
        elif self.color == "red":
            self.horizontal_velocity = 1
        elif self.color == "blue":
            self.vertical_velocity = 0.5

        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.x += self.horizontal_velocity
        if self.x >= (750 - 59) or self.x <= 0:
            self.horizontal_velocity *= -1
        self.y += vel + self.vertical_velocity

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 12, self.y, self.laser_img)
            self.laser.append(laser)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    # velocity of player and enemy
    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5
    laser_vel = 15

    player = Player(300, 600)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0, 0))
        # Draw text
        lives_label = main_font.render(f"Lives:{lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level:{level}", 1, (255, 255, 255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(
                    random.randrange(50, WIDTH - 100),
                    random.randrange(-1500, -100),
                    random.choice(["red", "blue", "green"]),
                )
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_vel > 0:  # Left
            player.x -= player_vel
        if (
            keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH
        ):  # Right
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0:  # Up
            player.y -= player_vel
        if (
            keys[pygame.K_DOWN]
            and player.y + player_vel + player.get_height() + 15 < HEIGHT
        ):  # Down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 240) == 1:
                enemy.shoot()
            if enemy.color == "red":
                random.randrange(0, 600)

            if enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
            elif collide(enemy, player):
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)


def main_menu():
    title_font = pygame.font.SysFont("comicsans", 60)
    title_font1 = pygame.font.SysFont("comicsans", 24)

    run = True
    in_menu = True
    while in_menu:
        WIN.blit(BG, (0, 0))
        title_label = title_font1.render( "Hello Player! To play the game you need to know some STRICT GUIDELINES!!",0.5,(255, 255, 255),)
        title1_label = title_font1.render( "UP ARROW for moving up", 0.5, (255, 255, 255))
        title2_label = title_font1.render("DOWN ARROW for moving down", 0.5, (255, 255, 255))
        title3_label = title_font1.render("LEFT ARROW for moving left", 0.5, (255, 255, 255))
        title4_label = title_font1.render("RIGHT ARROW for moving right", 0.5, (255, 255, 255))
        title5_label = title_font1.render("SPACE to shoot", 0.5, (255, 255, 255))
        title6_label = title_font1.render("You will have 5 lives", 0.5, (255, 255, 255))
        title7_label = title_font1.render( "You will LOSE A LIFE everytime you COLLIDE with an ENEMY or ENEMY EXITED the SCREEN!",0.5,(255, 255, 255),)
        title8_label = title_font1.render("You have a limited life! PLayer carefully as if it hits zero, then you die instantly!!", 0.5,(255, 255, 255),)
        title9_label = title_font1.render("CLICK THE MOUSE TO CONTINUE", 0.5,(255, 255, 255),)

        WIN.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2 - 60, 50))
        WIN.blit(title1_label, (WIDTH / 2 - title1_label.get_width() / 21 - 350, 120))
        WIN.blit(title2_label, (WIDTH / 2 - title2_label.get_width() / 2 - 235, 190))
        WIN.blit(title3_label, (WIDTH / 2 - title3_label.get_width() / 2 - 250, 260))
        WIN.blit(title4_label, (WIDTH / 2 - title4_label.get_width() / 2 - 241, 330))
        WIN.blit(title5_label, (WIDTH / 2 - title5_label.get_width() / 2 - 304, 400))
        WIN.blit(title6_label, (WIDTH / 2 - title6_label.get_width() / 2 - 289, 470))
        WIN.blit(title7_label, (WIDTH / 2 - title7_label.get_width() / 2, 540))
        WIN.blit(title8_label, (WIDTH / 2 - title7_label.get_width() / 2 - 2, 610))
        WIN.blit(title9_label, (WIDTH / 2 - title7_label.get_width() / 2 - 2, 680))


        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                in_menu = False

    while run:
        WIN.blit(BG, (0, 0))
        title_label = title_font.render(
            "Press the mouse to begin...", 1, (255, 255, 255)
        )
        WIN.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()

    pygame.quit()


main_menu()
