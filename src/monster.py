# src/monster.py
import pygame
from .settings import MONSTER_WIDTH, MONSTER_HEIGHT, MONSTER_HEALTH
from .settings import IMG_DIR

class Monster:
    def __init__(self, x, y):
        monster_image = pygame.image.load(f"{IMG_DIR}/monster.png").convert_alpha()
        monster_image = pygame.transform.scale(monster_image, (64, 64))#recizing
        self.image = monster_image
        self.rect = pygame.Rect(x, y, MONSTER_WIDTH, MONSTER_HEIGHT)
        self.health = MONSTER_HEALTH
        self.mask = pygame.mask.from_surface(self.image)

        self.in_collision = False  # to track quiz collisions

    def draw(self, surface):
        # If using an image with the correct size, you might do:
        surface.blit(self.image, self.rect)
        # If you had a mismatch in size, you'd rectify or scale appropriately

    def update(self):
        # (Optional) AI or idle movement
        pass
