import math
import random
import pygame

from src.settings import IMG_DIR


class Assistant(pygame.sprite.Sprite):
    def __init__(self, hero, x_offset=50, y_offset=-30, orbit_radius=70):
        super().__init__()
        self.hero = hero  # Reference to the hero so the sidekick can follow him
        self.x_offset = x_offset
        self.y_offset = y_offset
        # Load your sidekick image here
        self.image = pygame.image.load(f"{IMG_DIR}/assistant.png").convert_alpha()
        self.image = pygame.transform.scale(self.image,(48, 48))  # recizing
        self.rect = self.image.get_rect()
        # For dialogue: a timer and list of phrases
        self.dialogue_timer = 0
        self.current_dialogue = ""
        self.dialogues = ["Nice!", "Well done!", "Great job!", "Awesome!", "Keep it up!"]
        self.angle = random.uniform(0, 2 * math.pi)  # Start at a random angle
        self.angular_speed = random.choice(
            [-0.003, 0.003])  # Clockwise or anticlockwise rotation
        self.orbit_radius = orbit_radius

    def update(self):
        # Update the angle
        self.angle += self.angular_speed

        # Compute new position relative to the hero's center
        self.rect.centerx = self.hero.rect.centerx + math.cos(
            self.angle) * self.orbit_radius
        self.rect.centery = self.hero.rect.centery + math.sin(
            self.angle) * self.orbit_radius

        # Decrement the dialogue timer if active
        if self.dialogue_timer > 0:
            self.dialogue_timer -= 1

    def speak(self):
        # Set a dialogue phrase and a timer for how long it should be shown (e.g., 60 frames)
        self.current_dialogue = random.choice(self.dialogues)
        self.dialogue_timer = 240
    def explain(self):
        # TODO
        return

    def draw(self, surface, camera):
        # Get the assistant's screen position using the camera's transform
        screen_pos = camera.apply(self)
        surface.blit(self.image, screen_pos)
        if self.dialogue_timer > 0:
            font = pygame.font.SysFont(None, 24)
            text_surface = font.render(self.current_dialogue, True,
                                       (255, 255, 255))
            text_rect = text_surface.get_rect(center=(
            screen_pos[0] + self.rect.width // 2, screen_pos[1] - 20))
            surface.blit(text_surface, text_rect)