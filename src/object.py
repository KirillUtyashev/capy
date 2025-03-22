import pygame
from .settings import IMG_DIR
class Object:
    def __init__(self, name):
        self.name = name

    def interact(self, hero):
        pass  # To be overridden by child classes


class Cave(Object):
    def __init__(self, x, y):
        super().__init__("Cave")
        cave_image = pygame.image.load(f"{IMG_DIR}/cave.png").convert_alpha()
        cave_image = pygame.transform.scale(cave_image, (108, 108))#recizing
        self.image = cave_image # Assuming image is in assets directory
        self.rect = self.image.get_rect(topleft=(x, y))
        self.active = False

    def spawn(self):
        if not self.active:
            print("A cave has appeared after all monsters have been defeated!")
            self.active = True

    def interact(self, hero):
        if self.active:
            print(f"{hero.name} enters the cave...")
        else:
            print("The cave is not accessible yet.")


class Stone(Object):
    def __init__(self, x, y):
        super().__init__("Stone")
        stone_image = pygame.image.load(f"{IMG_DIR}/stone.png").convert_alpha()
        stone_image = pygame.transform.scale(stone_image, (64, 64))#recizing
        self.image = stone_image # Assuming image is in assets directory
        self.rect = self.image.get_rect(topleft=(x, y))
