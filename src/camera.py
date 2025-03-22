# import pygame
#
# class Camera:
#     def __init__(self, width, height):
#         self.camera_rect = pygame.Rect(0, 0, width, height)
#         self.world_width = width
#         self.world_height = height
#
#     def apply(self, target_rect):
#         return target_rect.move(-self.camera_rect.topleft)
#
#     def update(self, target):
#         x = target.rect.centerx - self.camera_rect.width // 2
#         y = target.rect.centery - self.camera_rect.height // 2
#
#         # Clamp camera so it doesn't go out of world bounds
#         x = max(0, min(x, self.world_width - self.camera_rect.width))
#         y = max(0, min(y, self.world_height - self.camera_rect.height))
#
#         self.camera_rect.topleft = (x, y)
