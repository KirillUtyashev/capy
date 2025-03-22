# src/hero.py
import pygame
from .settings import HERO_HEALTH, HERO_SPEED
from .settings import IMG_DIR, TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, GRID_ORIGIN_X, GRID_ORIGIN_Y

class Hero:
    def __init__(self, x, y):
        # Load knight image
        knight_image = pygame.image.load(f"{IMG_DIR}/knight.png").convert_alpha()
        knight_image = pygame.transform.scale(knight_image, (64, 64))#recizing
        knight_attack_image = pygame.image.load(f"{IMG_DIR}/knight_attack.png")
        knight_attack_image = pygame.transform.scale(knight_attack_image,
                                              (64, 64))  # recizing
        self.attack_image = knight_attack_image
        self.normal_image = knight_image
        self.image = knight_image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = x
        self.rect.y = y
        self.health = HERO_HEALTH
        self.speed = HERO_SPEED
        self.attack_timer = 0  # Counter for attack frame
        self.attack_flag = 0
        self.chill_timer = 0
        # Additional states (e.g., in_collision with monster)

    def move(self, dx, dy, stone_rects):
    # Try horizontal move
        new_x = self.rect.x + dx
        self.rect.x = new_x
        if any(self.rect.colliderect(stone) for stone in stone_rects):
            self.rect.x -= dx  # Cancel move if hitting a stone

        # Try vertical move
        new_y = self.rect.y + dy
        self.rect.y = new_y
        if any(self.rect.colliderect(stone) for stone in stone_rects):
            self.rect.y -= dy  # Cancel move if hitting a stone

    def attack(self):
        self.attack_timer = 30


    def update_position_from_rect(self):
        self.x = self.rect.x
        self.y = self.rect.y


    def update(self, keys, stone_rects):
        # Simple movement logic
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx = -self.speed
        if keys[pygame.K_RIGHT]:
            dx = self.speed
        if keys[pygame.K_UP]:
            dy = -self.speed
        if keys[pygame.K_DOWN]:
            dy = self.speed

        self.move(dx, dy, stone_rects)
        # Check horizontal movement

        if self.attack_timer > 0:
            self.attack_timer -= 1
            if self.attack_timer < 10 or self.attack_timer > 20:
                self.image = self.attack_image
            else:
                self.image = self.normal_image
        else:
            self.image = self.normal_image

    def draw(self, surface):
        surface.blit(self.image, self.rect)
