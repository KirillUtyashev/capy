import math
import random
import sys

import pygame

from src.settings import IMG_DIR


class Assistant(pygame.sprite.Sprite):
    def __init__(self, hero, x_offset=50, y_offset=-30, orbit_radius=70):
        super().__init__()
        self.hero = hero  # Reference to the hero so the assistant can follow him
        self.x_offset = x_offset
        self.y_offset = y_offset
        # Load and resize the assistant image
        self.image = pygame.image.load(f"{IMG_DIR}/assistant.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (24, 24))
        self.rect = self.image.get_rect()
        # Dialogue properties
        self.dialogue_timer = 0
        self.current_dialogue = ""
        self.dialogues = ["Nice!", "Well done!", "Great job!", "Awesome!", "Keep it up!"]
        # Orbiting properties
        self.angle = random.uniform(0, 2 * math.pi)  # Start at a random angle
        self.angular_speed = random.choice([-0.003, 0.003])  # Clockwise or anticlockwise
        self.orbit_radius = orbit_radius

    def update(self):
        # Update the orbiting angle
        self.angle += self.angular_speed

        # Compute new position relative to the hero's center using circular motion
        self.rect.centerx = self.hero.rect.centerx + math.cos(self.angle) * self.orbit_radius
        self.rect.centery = self.hero.rect.centery + math.sin(self.angle) * self.orbit_radius

        # Decrement the dialogue timer if active
        if self.dialogue_timer > 0:
            self.dialogue_timer -= 1

    def speak(self):
        # Choose a random dialogue and set a timer (e.g., 240 frames)
        self.current_dialogue = random.choice(self.dialogues)
        self.dialogue_timer = 240

    def draw(self, surface, camera):
        # Get the assistant's screen position via the camera transformation
        screen_pos = camera.apply(self)
        surface.blit(self.image, screen_pos)
        # Draw the dialogue if the timer is active
        if self.dialogue_timer > 0:
            self.draw_speech_bubble(surface, screen_pos)

    def draw_speech_bubble(self, surface, screen_pos):
        # Draw a visually appealing speech bubble for the current dialogue
        font = pygame.font.SysFont(None, 24)
        text_surface = font.render(self.current_dialogue, True, (255, 255, 255))
        # Center the text above the assistant sprite
        text_rect = text_surface.get_rect(
            center=(screen_pos[0] + self.rect.width // 2, screen_pos[1] - 30)
        )
        # Create a bubble by inflating the text rect
        bubble_rect = text_rect.inflate(20, 20)
        # Draw bubble background and border with rounded corners
        pygame.draw.rect(surface, (50, 50, 50), bubble_rect, border_radius=8)
        pygame.draw.rect(surface, (255, 255, 255), bubble_rect, 2, border_radius=8)
        surface.blit(text_surface, text_rect)
