# src/game.py
import pygame
import sys

from .settings import WIDTH, HEIGHT, FPS, BLACK, WHITE
from .settings import IMG_DIR
from .hero import Hero
from .monster import Monster
from .quiz import show_quiz
from .utils import reposition_hero, get_random_grid_position, get_random_spawn_positions, get_valid_spawn_positions
from .object import Cave, Stone
import random
from .settings import TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, GRID_ORIGIN_X, GRID_ORIGIN_Y

def draw_health_bar(surface, x, y, current_health, max_health, bar_width=100, bar_height=10, color=(0, 255, 0)):
    """
    Draws a health bar on 'surface' with top-left at (x, y).
    The bar shows 'current_health' out of 'max_health'.
    bar_width, bar_height define the size of the bar.
    'color' is the fill color.
    """
    # Draw a border (white rect)
    pygame.draw.rect(surface, (255, 255, 255), (x, y, bar_width, bar_height), 2)

    # Calculate filled width
    fill_ratio = current_health / max_health
    if fill_ratio < 0:
        fill_ratio = 0
    fill_width = int(bar_width * fill_ratio)

    # Draw the filled part
    inner_rect = pygame.Rect(x, y, fill_width, bar_height)
    pygame.draw.rect(surface, color, inner_rect)



class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Dungeon Crawler - Quiz Edition")
        self.dungeon_tile = pygame.image.load(f"{IMG_DIR}/dungeon_tile.png").convert()
        self.dungeon_tile = pygame.transform.scale(self.dungeon_tile, (64, 64))

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 30)
        self.exit_button_rect = pygame.Rect(WIDTH - 140, 10, 120, 50)
        self.cave = None
        # self.shadow_surface = pygame.Surface((WIDTH, HEIGHT))
        # self.shadow_surface.set_colorkey((0, 0, 0))  # Make black fully transparent if needed
        # self.shadow_surface.set_alpha(220)  # Adjust darkness (0 = invisible, 255 = fully black)
        self.stones = []
        self.spawn_border_stones()
        self.stone_positions = [stone.rect.topleft for stone in self.stones]
        # Create hero, monsters
        hero_pos = get_random_spawn_positions(1,exclude=self.stone_positions)[0]
        self.hero = Hero(*hero_pos)
        hero_tile = (self.hero.rect.x - GRID_ORIGIN_X) // TILE_SIZE, (self.hero.rect.y - GRID_ORIGIN_Y) // TILE_SIZE
        monster_exclude = self.stone_positions + [hero_pos]
        monster_positions = get_random_spawn_positions(2, exclude=monster_exclude)
        self.monsters = [Monster(x, y) for (x, y) in monster_positions]
        self.stones = []
        self.spawn_border_stones()

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.exit_button_rect.collidepoint(mouse_pos):
                        # End the game
                        running = False


            # === Update logic ===
            keys = pygame.key.get_pressed()
            self.hero.update(keys)

            # Monster collisions => quiz
            self.check_collisions()

            # Remove dead monsters
            self.monsters = [m for m in self.monsters if m.health > 0]
            if not self.monsters and self.cave is None:
                self.spawn_cave()
            # If hero dead => exit or show game over
            if self.hero.health <= 0:
                print("You died!")
                running = False

            # === Draw everything ===
            self.screen.fill(BLACK)
            self.draw_dungeon_floor()

            self.hero.draw(self.screen)
            for stone in self.stones:
                self.screen.blit(stone.image, stone.rect)
            for m in self.monsters:
                m.draw(self.screen)
            # self.draw_shadow()
            self.draw_hud()
            # HUD
            health_text = self.font.render(f"Hero HP: {self.hero.health}", True, WHITE)
            self.screen.blit(health_text, (10, 10))
            if self.cave and self.cave.active:
                self.screen.blit(self.cave.image, self.cave.rect)

            if self.cave and self.cave.active and self.hero.rect.colliderect(self.cave.rect):
                self.cave.interact(self.hero)

            # monster_text = self.font.render(f"Monsters: {len(self.monsters)}", True, WHITE)
            # self.screen.blit(monster_text, (10, 40))
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    # def check_collisions(self):
    #     """If hero collides with monster and it’s a new collision, show quiz."""
    #     for m in self.monsters:
    #         if self.hero.rect.colliderect(m.rect):
    #             if not m.in_collision:
    #                 m.in_collision = True
    #                 result = show_quiz(self.screen, self.clock, self.font)
    #                 if result:
    #                     m.health -= 1
    #                 else:
    #                     self.hero.health -= 1
    #                 reposition_hero(self.hero, m, distance=100)
    #         else:
    #             m.in_collision = False
    def check_collisions(self):
        """If hero collides with monster and it’s a new collision, show quiz."""
        for m in self.monsters:
            if self.hero.rect.colliderect(m.rect):
                # Now check pixel-perfect collision
                offset = (m.rect.x - self.hero.rect.x, m.rect.y - self.hero.rect.y)
                if self.hero.mask.overlap(m.mask, offset):
                    if not m.in_collision:
                        m.in_collision = True
                        result = show_quiz(self.screen, self.clock, self.font)
                        if result:
                            m.health -= 1
                        else:
                            self.hero.health -= 1
                        reposition_hero(self.hero, m, distance=100)
                else:
                    m.in_collision = False
            else:
                m.in_collision = False




    def draw_hud(self):
        """
        Draws the hero's health bar and each monster's health bar at the top.
        """
        # Hero health bar at (10, 10)
        # 2) Draw the exit button rectangle
        pygame.draw.rect(self.screen, (150, 50, 50), self.exit_button_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), self.exit_button_rect, 2)

        # "Exit" label
        exit_label = self.font.render("EXIT", True, (255, 255, 255))
        label_rect = exit_label.get_rect(center=self.exit_button_rect.center)
        self.screen.blit(exit_label, label_rect)

        draw_health_bar(
            surface=self.screen,
            x=10,
            y=30,
            current_health=self.hero.health,
            max_health=10,  # or whatever your hero's max health is
            bar_width=150,
            bar_height=15,
            color=(0, 255, 0)  # green for hero
        )

        # Label "Hero" above the bar
        # hero_label = self.font.render("Hero", True, (255, 255, 255))
        # self.screen.blit(hero_label, (10, 10 - 20))

        # Monster health bars stacked below hero
        bar_x_start = 180
        bar_y = 30
        bar_width = 120
        bar_height = 10
        spacing = 10

        for i, monster in enumerate(self.monsters):
            # Calculate each monster bar’s x-position in a row
            bar_x = bar_x_start + i * (bar_width + spacing)

            # Draw the monster bar horizontally
            draw_health_bar(
                surface=self.screen,
                x=bar_x,
                y=bar_y,
                current_health=monster.health,
                max_health=3,        # or your actual MONSTER_HEALTH
                bar_width=bar_width,
                bar_height=bar_height,
                color=(255, 0, 0)    # red for monster
            )

            # Label "Monster i" just above each bar
            label = self.font.render(f"Monster {i+1}", True, (255, 255, 255))
            self.screen.blit(label, (bar_x, bar_y - 18))
    def spawn_cave(self):
        self.cave = Cave(300, 300)  # Set position as needed
        self.cave.spawn()

    def draw_dungeon_floor(self):
        for x in range(100, 1001, 64):  # 100 to 1000 inclusive, step by TILE_SIZE
            for y in range(100, 1001, 64):
                self.screen.blit(self.dungeon_tile, (x, y))
    # def draw_shadow(self):
    # # Create a full-screen black transparent surface
    #     self.shadow_surface = pygame.Surface((WIDTH, HEIGHT), flags=pygame.SRCALPHA)
    #     self.shadow_surface.fill((0, 0, 0, 255))  # 220 = mostly dark
    #
    #     # Punch a transparent circle where the hero stands
    #     light_radius = 5 * TILE_SIZE  # Adjust as needed
    #     light_center = self.hero.rect.center
    #
    #     pygame.draw.circle(self.shadow_surface, (0, 0, 0, 0), light_center, light_radius)
    #
    #     # Draw the shadow on top of everything
    #     self.screen.blit(self.shadow_surface, (0, 0))
    def spawn_border_stones(self):
        x_min = 100
        x_max = 1000
        y_min = 100
        y_max = 1000

        # Top and bottom rows (y = 100 and y = 1000)
        for x in range(x_min, x_max + 1, TILE_SIZE):
            self.stones.append(Stone(x, y_min))   # Top edge
            self.stones.append(Stone(x, y_max))   # Bottom edge

        # Left and right columns (x = 100 and x = 1000)
        for y in range(y_min + TILE_SIZE, y_max, TILE_SIZE):  # skip corners (already placed)
            self.stones.append(Stone(x_min, y))  # Left edge
            self.stones.append(Stone(x_max, y))  # Right edge
