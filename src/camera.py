# camera.py
import pygame


class Camera:
    def __init__(self, world_width, world_height, screen_width, screen_height):
        self.world_width = world_width
        self.world_height = world_height
        self.screen_width = screen_width
        self.screen_height = screen_height
        # This rect represents the camera's viewport on the world
        self.camera_rect = pygame.Rect(0, 0, screen_width, screen_height)

    def apply(self, entity):
        """
        Adjust the entity's rectangle by subtracting the camera's position,
        so that drawing is relative to the current viewport.
        """
        return entity.rect.move(-self.camera_rect.x, -self.camera_rect.y)

    def update(self, target):
        """
        Center the camera on the target (e.g. the player).
        Optionally, clamp the camera so it doesn't scroll outside the world boundaries.
        """
        # Center the camera on the target
        x = target.rect.centerx - self.screen_width // 2
        y = target.rect.centery - self.screen_height // 2

        # Clamp the camera's position so it stays within the world limits
        x = max(0, min(x, self.world_width - self.screen_width))
        y = max(0, min(y, self.world_height - self.screen_height))

        self.camera_rect.topleft = (x, y)
