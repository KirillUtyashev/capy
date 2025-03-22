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
            pygame.time.delay(300)  # Optional delay for clarity

            from .game import Game  # avoid circular import issues
            cave_game = Game(in_cave=True)  # pass flag
            cave_game.run()

            pygame.quit()


class Potion(Object):
    def __init__(self, x, y):
        super().__init__("Potion")
        potion_image = pygame.image.load(f"{IMG_DIR}/potion.png").convert_alpha()
        potion_image = pygame.transform.scale(potion_image, (108, 108))#recizing
        self.image = potion_image # Assuming image is in assets directory
        self.rect = self.image.get_rect(topleft=(x, y))
        self.active = False

    def spawn(self):
        if not self.active:
            print("A potion has appeared after all monsters have been defeated!")
            self.active = True

    def interact(self, hero):
        if self.active:
            print("potion...")
            self.active = False
        else:
            print("The potion is not accessible yet.")


class Stone(Object):
    def __init__(self, x, y):
        super().__init__("Stone")
        stone_image = pygame.image.load(f"{IMG_DIR}/stone.png").convert_alpha()
        stone_image = pygame.transform.scale(stone_image, (64, 64))#recizing
        self.image = stone_image # Assuming image is in assets directory
        self.rect = self.image.get_rect(topleft=(x, y))


class Button():
    def __init__(self, image, pos, text_input, font, base_color, hovering_color):
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def update(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            return True
        return False

    def changeColor(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)
