# src/monster.py
import math
import hashlib
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

    def move_towards_player(self, hero, all_monsters, speed=1, safe_distance=100):
        """
        Moves the monster towards the hero while maintaining a safe distance from all other monsters.
        safe_distance: minimum gap (in pixels) required between monsters.
        """
        # Calculate the vector from self to hero.
        dx = hero.rect.x - self.rect.x
        dy = hero.rect.y - self.rect.y
        dist = math.hypot(dx, dy)
        if dist == 0:
            return  # Prevent division by zero if they overlap.

        # Normalize the vector and scale by the desired speed.
        dx, dy = (dx / dist) * speed, (dy / dist) * speed

        # Create a candidate rectangle for the new position.
        new_rect = self.rect.copy()
        new_rect.x += dx
        new_rect.y += dy

        # Define a helper function to check collisions with a safety buffer.
        def collides(rect):
            for monster in all_monsters:
                if monster != self:
                    # Inflate the other monster's rect by safe_distance*2 (30 pixels on each side).
                    inflated_rect = monster.rect.inflate(safe_distance * 2, safe_distance * 2)
                    if rect.colliderect(inflated_rect):
                        return True
            return False

        # Check if the full move would result in a collision.
        if not collides(new_rect):
            self.rect.x += dx
            self.rect.y += dy
        else:
            # If a collision is detected, try to slide along each axis.
            # Check horizontal movement only.
            temp_rect = self.rect.copy()
            temp_rect.x += dx
            collision_x = collides(temp_rect)

            # Check vertical movement only.
            temp_rect = self.rect.copy()
            temp_rect.y += dy
            collision_y = collides(temp_rect)

            # Move along any axis that is clear.
            if not collision_x:
                self.rect.x += dx
            if not collision_y:
                self.rect.y += dy
