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
        self.mask = pygame.mask.from_surface(self.image)
        self.health = MONSTER_HEALTH
        self.stun_timer = 0


        self.in_collision = False  # to track quiz collisions

    def draw(self, surface):
        # If using an image with the correct size, you might do:
        surface.blit(self.image, self.rect)
        # If you had a mismatch in size, you'd rectify or scale appropriately

    def update(self):
        # (Optional) AI or idle movement
        pass

    def move_towards_player(self, hero, all_monsters, stones, speed=1, safe_distance=100):
        """
        Moves the monster towards the hero while maintaining a safe distance from all other monsters.
        safe_distance: minimum gap (in pixels) required between monsters.
        """
        if self.stun_timer > 0:
            self.stun_timer -= 1
            return

        # Calculate the vector from self to hero.
        dx = hero.rect.x - self.rect.x
        dy = hero.rect.y - self.rect.y
        dist = math.hypot(dx, dy)
        if dist == 0:
            return

        dx, dy = (dx / dist) * speed, (dy / dist) * speed

        candidate_rect = self.rect.copy()
        candidate_rect.x += dx
        candidate_rect.y += dy

        def collides_with_monsters(rect):
            for monster in all_monsters:
                if monster != self:
                    inflated_rect = monster.rect.inflate(safe_distance, safe_distance)
                    if rect.colliderect(inflated_rect):
                        return True
            return False

        def collides_with_stones(rect):
            for stone in stones:
                if rect.colliderect(stone.rect):
                    return True
            return False

        # Check if the full move is clear of both monster and stone collisions.
        if not collides_with_monsters(candidate_rect) and not collides_with_stones(candidate_rect):
            self.rect.x += dx
            self.rect.y += dy
        else:
            # If the full move would collide, try sliding along each axis separately.
            # Horizontal move only.
            horizontal_rect = self.rect.copy()
            horizontal_rect.x += dx
            # Vertical move only.
            vertical_rect = self.rect.copy()
            vertical_rect.y += dy

            # Slide: if horizontal move is valid, update x.
            if not collides_with_monsters(horizontal_rect) and not collides_with_stones(horizontal_rect):
                self.rect.x += dx
            # Slide: if vertical move is valid, update y.
            if not collides_with_monsters(vertical_rect) and not collides_with_stones(vertical_rect):
                self.rect.y += dy
