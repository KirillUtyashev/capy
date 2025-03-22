# src/hero.py
import pygame
from .settings import HERO_HEALTH, HERO_SPEED
from .settings import IMG_DIR, TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, GRID_ORIGIN_X, GRID_ORIGIN_Y

class Hero:
    def __init__(self, x, y):
        # Load knight image
        knight_image = pygame.image.load(f"{IMG_DIR}/knight.png").convert_alpha()
        knight_image = pygame.transform.scale(knight_image, (64, 64))#recizing
        self.image = knight_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)
        self.health = HERO_HEALTH
        self.speed = HERO_SPEED

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

    def draw(self, surface):
        surface.blit(self.image, self.rect)
