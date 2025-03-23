# src/game.py
import itertools
import json
import time
import asyncio
import pygame
import sys
import multiprocessing
from .cohere_ai import explain_mistake, generate_questions
from .queue import Queue
from multiprocessing.connection import Connection
from .settings import WIDTH, HEIGHT, FPS, BLACK, WHITE
from .settings import IMG_DIR
from .hero import Hero
from .monster import Monster
from .quiz import show_quiz
from .utils import reposition_hero, get_random_grid_position, get_random_spawn_positions, get_valid_spawn_positions
from .object import Cave, Stone, Button, Potion
from .dungeon import Dungeon
from .assistant import Assistant
import random
from .settings import (TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, GRID_ORIGIN_X,
                       GRID_ORIGIN_Y, MONSTER_SPEED, STUN_1_TIME, NUM_MONSTERS)
from .camera import Camera



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


TOPIC = None


def run_generate_question(topic, num, stop_event, result_queue):
    result = generate_questions(topic, n=num)
    result_queue.put(result)
    stop_event.set()  # Signal that question generation is complete


class Game:
    def __init__(self, in_cave=False):
        self.theme=random.choice([["dungeon",f"{IMG_DIR}/dungeon_tile.png",f"{IMG_DIR}/monster.png", f"{IMG_DIR}/stone.png"], ["sea",f"{IMG_DIR}/bubbles.png",f"{IMG_DIR}/blue_mon.png", f"{IMG_DIR}/bubbl.png"], ["grass", f"{IMG_DIR}/grass.png", f"{IMG_DIR}/tree_mon.png", f"{IMG_DIR}/tre.png"]])
        self.in_cave = in_cave
        pygame.init()
        try:
            if in_cave:
                pygame.mixer.music.load("assets/music/run-faster-abbynoise-main-version-36307-02-27.mp3")
                pygame.mixer.music.play(-1)
            else:
                pygame.mixer.music.load("assets/music/open-fields-aaron-paul-low-main-version-25198-02-16.mp3")
                pygame.mixer.music.play(-1)
        except Exception as e:
            print("Audio error:", e)
        print("In the game")
        self.dungeon = Dungeon()
        self.island_map = self.dungeon.get_island_only()
        self.world_width = len(self.island_map[0]) * TILE_SIZE + 100  # width in pixels
        self.world_height = len(self.island_map) * TILE_SIZE + 100
        self.base_surface = pygame.Surface((WIDTH, HEIGHT))  # Draw game here
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Dungeon Crawler - Quiz Edition")
        print(self.theme[1])
        self.dungeon_tile = pygame.image.load(self.theme[1]).convert()
        self.dungeon_tile = pygame.transform.scale(self.dungeon_tile, (64, 64))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 30)
        self.exit_button_rect = pygame.Rect(WIDTH - 140, 10, 120, 50)
        self.cave = None
        self.potion= None
        # self.shadow_surface = pygame.Surface((WIDTH, HEIGHT))
        # self.shadow_surface.set_colorkey((0, 0, 0))  # Make black fully transparent if needed
        # self.shadow_surface.set_alpha(220)  # Adjust darkness (0 = invisible, 255 = fully black)
        # Create hero, monsters
        island_tiles = []
        for row in range(len(self.island_map)):
            for col in range(len(self.island_map[0])):
                if self.island_map[row][col] == 1:
                    x = 100 + col * TILE_SIZE
                    y = 100 + row * TILE_SIZE
                    island_tiles.append((x, y))
        self.spawn_border_stones()
        self.stone_positions = [stone.rect.topleft for stone in self.stones]
        self.hero = Hero(164, 164)
        self.assistant = Assistant(self.hero)
        self.camera = Camera(WIDTH, HEIGHT, self.world_width, self.world_height)
        monster_exclude = self.stone_positions

        if in_cave:
            global NUM_MONSTERS
            NUM_MONSTERS = NUM_MONSTERS * 2
        monster_positions = get_random_spawn_positions(self.dungeon, NUM_MONSTERS, exclude=monster_exclude,offset_x=100,
                                                       offset_y=100)
        self.monsters = [Monster(x, y, self.theme) for (x, y) in monster_positions]
        if in_cave:
            self.questions = Queue()
            with open("src/questions.json", "r") as f:
                data = json.load(f)
            self.questions.read_from_json(data)
        else:
            self.questions = None
        self.topic = TOPIC

    def initialize_theme(self, topic=None):
        global TOPIC
        if not TOPIC:
            TOPIC = topic
        self.topic = TOPIC
        self.questions = self.run_generate_with_loading()

    def run(self):
        background = pygame.image.load("assets/images/terrace.png")
        self.screen.blit(background, (0, 0))
        running = True
        while running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h),
                                                          pygame.RESIZABLE)
                    new_width, new_height = event.w, event.h

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.exit_button_rect.collidepoint(mouse_pos):
                        # End the game
                        running = False

            # === Update logic ===
            keys = pygame.key.get_pressed()
            stone_rects = [stone.rect for stone in self.stones]
            self.hero.update(keys, stone_rects)
            self.assistant.update()
            self.camera.update(self.hero)
            self.check_stone_collisions()

            # Monster collisions => quiz
            asyncio.run(self.check_collisions())

            # Remove dead monsters
            self.monsters = [m for m in self.monsters if m.health > 0]
            if not self.monsters and self.cave is None:
                self.spawn_cave()
            if len(self.monsters)==1 and self.potion is None:
                self.spawn_potion()
            # If hero dead => exit or show game over
            if self.hero.health <= 0:
                print("You died!")
                running = False

            # === Draw everything ===
            background = pygame.image.load("assets/images/terrace.png")
            self.screen.blit(background, (0, 0))
            self.draw_dungeon_floor()

            # self.hero.draw(self.base_surface)
            # # self.draw_shadow()

            self.base_surface.blit(self.hero.image,
                                   self.camera.apply(self.hero))
            for stone in self.stones:
                self.base_surface.blit(stone.image, self.camera.apply(stone))
            for monster in self.monsters:
                monster.move_towards_player(hero=self.hero, all_monsters=self.monsters, speed=MONSTER_SPEED, stones=self.stones)
                self.base_surface.blit(monster.image, self.camera.apply(monster))
            if self.potion and self.potion.active:
                self.base_surface.blit(self.potion.image, self.camera.apply(self.potion))
            if self.cave and self.cave.active:
                self.base_surface.blit(self.cave.image,
                                       self.camera.apply(self.cave))
            self.assistant.draw(self.base_surface, self.camera)
            self.draw_hud()
            # HUD
            health_text = self.font.render(f"Hero HP: {self.hero.health}", True, WHITE)
            self.base_surface.blit(health_text, (10, 10))

            if self.cave and self.cave.active and self.hero.rect.colliderect(self.cave.rect):
                self.cave.interact(self.hero)
            if self.potion and self.potion.active and self.hero.rect.colliderect(self.potion):
                self.potion.interact(self.hero)
                self.hero.health+=1

            # monster_text = self.font.render(f"Monsters: {len(self.monsters)}", True, WHITE)
            # self.screen.blit(monster_text, (10, 40))
            self.draw_scaled_game()
            pygame.display.flip()

        # pygame.quit()
        self.main_menu()
        # sys.exit()

    def get_font(self, size): # Returns Press-Start-2P in the desired size
        return pygame.font.Font("assets/font.ttf", size)

    def choose_prompt(self):
        background = pygame.image.load("assets/images/background.png")
        screen_width, screen_height = self.screen.get_size()  # Get screen dimensions
        topic = ""  # This will store the user's text input
        input_active = True

        padding_top = 180  # Adjust this to move everything lower

        while input_active:
            self.clock.tick(FPS)
            self.screen.blit(background, (0, 0))

            # Header Text - Centered with Padding
            header_text = self.get_font(30).render("Please enter a topic to study...", True, "#000435")  # Softer gold color
            header_rect = header_text.get_rect(center=(screen_width // 2, screen_height // 4 + padding_top))
            self.screen.blit(header_text, header_rect)

            # Input Box - Centered with Padding
            input_box_width = 640
            input_box_height = 60
            padding_bottom=20
            input_box_x = (screen_width - input_box_width) // 2
            input_box_y = screen_height // 2 + padding_bottom

            input_box_rect = pygame.Rect(input_box_x, input_box_y, input_box_width, input_box_height)
            pygame.draw.rect(self.screen, (255, 255, 255), input_box_rect, 2)

            # Render User Input Text - Centered inside box
            input_text_surf = self.get_font(50).render(topic, True, "#000435")
            input_text_rect = input_text_surf.get_rect(midleft=(input_box_rect.x + 10, input_box_rect.centery))
            self.screen.blit(input_text_surf, input_text_rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    input_active = False
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        print("User Input:", topic)
                        input_active = False  # or trigger another action/transition
                    elif event.key == pygame.K_BACKSPACE:
                        topic = topic[:-1]
                    else:
                        topic += event.unicode

            pygame.display.update()
        self.initialize_theme(topic)
        self.run()

    def main_menu(self):
        print("I'm init")
        background = pygame.image.load("assets/images/background.png")
        screen_width, screen_height = self.screen.get_size()  # Get dynamic screen size

        padding_top = 150  # Adjust this to move everything lower
        button_offset = 100  # Additional spacing for buttons

        while True:
            self.clock.tick(FPS)
            self.screen.blit(background, (0, 0))

            MENU_MOUSE_POS = pygame.mouse.get_pos()

            # Adjusted Header Position with New Color
            MENU_TEXT = self.get_font(75).render("Educonquest", True, "#000435")  # Softer gold color
            MENU_RECT = MENU_TEXT.get_rect(center=(screen_width // 2, 100 + padding_top))

            button_image = pygame.image.load("assets/images/text.png")

            # Lowered Button Positions
            PLAY_BUTTON = Button(image=button_image, pos=(screen_width // 2, 250 + padding_top + button_offset),
                                 text_input="PLAY", font=self.get_font(75), base_color="#d7fcd4",
                                 hovering_color="White")
            OPTIONS_BUTTON = Button(image=button_image, pos=(screen_width // 2, 400 + padding_top + button_offset),
                                    text_input="OPTIONS", font=self.get_font(50), base_color="#d7fcd4",
                                    hovering_color="White")
            QUIT_BUTTON = Button(image=button_image, pos=(screen_width // 2, 550 + padding_top + button_offset),
                                 text_input="QUIT", font=self.get_font(60), base_color="#d7fcd4",
                                 hovering_color="White")

            self.screen.blit(MENU_TEXT, MENU_RECT)

            for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
                button.changeColor(MENU_MOUSE_POS)
                button.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                        self.choose_prompt()
                    if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                        self.run()
                    if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                        pygame.quit()
                        sys.exit()

            pygame.display.update()

    async def check_collisions(self):
        """If hero collides with monster, and it’s a new collision, show quiz."""
        temp_questions = Queue()
        for m in self.monsters:
            if m.stun_timer > 0:
                continue
            else:
                m.in_collision = False
            if self.hero.rect.colliderect(m.rect):
                # Now check pixel-perfect collision
                offset = (m.rect.x - self.hero.rect.x, m.rect.y - self.hero.rect.y)
                if self.hero.mask.overlap(m.mask, offset):
                    if not m.in_collision:
                        m.in_collision = True
                        # Gotta make sure queue is not empty
                        question = self.questions.dequeue()
                        print(len(self.questions), NUM_MONSTERS)
                        if len(self.questions) == NUM_MONSTERS // 2:
                            print("async")
                            temp_questions = await asyncio.to_thread(generate_questions, self.topic, NUM_MONSTERS)
                        ans = show_quiz(self.base_surface, self.clock, self.font, question)
                        if ans == question["correct"]:
                            m.health -= 1
                            self.hero.attack()
                            m.damaged = True
                            self.assistant.speak()
                        else:
                            self.hero.health -= 1
                            self.hero.take_damage()

                        m.stun_timer = STUN_1_TIME
                        # reposition_hero(self.hero, m, distance=100)
                else:
                    m.in_collision = False
            else:
                m.in_collision = False
        while not temp_questions.is_empty():
            self.questions.enqueue(temp_questions.dequeue())

    def draw_scaled_game(self):
        # Get the actual window size.
        display_width, display_height = self.screen.get_size()
        # Calculate scale factors based on your fixed game dimensions.
        scale_w = display_width / WIDTH
        scale_h = display_height / HEIGHT
        # Use the smaller scale factor to preserve the aspect ratio.
        scale = min(scale_w, scale_h)
        scaled_width = int(WIDTH * scale)
        scaled_height = int(HEIGHT * scale)

        # Scale the base_surface (which is drawn in fixed dimensions).
        scaled_surface = pygame.transform.scale(self.base_surface,
                                                (scaled_width, scaled_height))

        # Compute offsets to center the game view.
        x_offset = (display_width - scaled_width) // 2
        y_offset = (display_height - scaled_height) // 2

        # Optionally clear the screen to a background color (BLACK in this case).
        background = pygame.image.load("assets/images/terrace.png")
        self.screen.blit(background, (0, 0))
        self.screen.blit(scaled_surface, (x_offset, y_offset))


    def draw_hud(self):
        """
        Draws the hero's health bar and each monster's health bar at the top.
        """
        # Hero health bar at (10, 10)
        # 2) Draw the exit button rectangle
        pygame.draw.rect(self.base_surface, (150, 50, 50), self.exit_button_rect)
        pygame.draw.rect(self.base_surface, (255, 255, 255), self.exit_button_rect, 2)

        # "Exit" label
        exit_label = self.font.render("EXIT", True, (255, 255, 255))
        label_rect = exit_label.get_rect(center=self.exit_button_rect.center)
        self.base_surface.blit(exit_label, label_rect)

        draw_health_bar(
            surface=self.base_surface,
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
                surface=self.base_surface,
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
            self.base_surface.blit(label, (bar_x, bar_y - 18))

    def spawn_cave(self):
        # 1) Pick a random valid position for the cave
        #    (i.e., on island cells, excluding stone positions, etc.)
        cave_positions = get_random_spawn_positions(
            self.dungeon,           # the Dungeon instance
            count=1,                # just 1 random spot for the cave
            exclude=self.stone_positions,  # optional; exclude stone positions
            tile_size=TILE_SIZE,
            offset_x=100,           # match whatever offset you're using
            offset_y=100
        )

        # 2) Create the cave at that position
        x, y = cave_positions[0]
        self.cave = Cave(x, y)
        self.cave.spawn()

    def spawn_potion(self):
        pos=get_random_spawn_positions(self.dungeon,1, exclude=self.stone_positions)
        self.potion = Potion(pos[0][0],pos[0][1])
        self.potion.spawn()

    def draw_dungeon_floor(self):
        for row in range(len(self.island_map)):
            for col in range(len(self.island_map[0])):
                if self.island_map[row][col] == 1:
                    # Convert grid coords to screen coords
                    x = 100 + col * TILE_SIZE
                    y = 100 + row * TILE_SIZE

                    tile_pos = (x - self.camera.camera_rect.x,
                                y - self.camera.camera_rect.y)
                    self.base_surface.blit(self.dungeon_tile, tile_pos)

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
        self.stones = []

        rows = len(self.island_map)
        cols = len(self.island_map[0])

        for row in range(rows):
            for col in range(cols):
                if self.island_map[row][col] == 1:
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = row + dr, col + dc
                        if not (0 <= nr < rows and 0 <= nc < cols) or self.island_map[nr][nc] == 0:
                            # Edge of island
                            x = 100 + col * TILE_SIZE
                            y = 100 + row * TILE_SIZE
                            self.stones.append(Stone(x, y, self.theme))
                            break  # only place one stone per tile


    # def draw_dungeon_floor(self):
    #     for row in range(len(self.island_map)):
    #         for col in range(len(self.island_map[0])):
    #             if self.island_map[row][col] == 1:
    #                 # Convert grid coords to screen coords
    #                 x = 100 + col * TILE_SIZE
    #                 y = 100 + row * TILE_SIZE
    #
    #                 tile_pos = (x - self.camera.camera_rect.x,
    #                             y - self.camera.camera_rect.y)
    #                 self.base_surface.blit(self.dungeon_tile, tile_pos)
    def check_stone_collisions(self):
        for stone in self.stones:
            if self.hero.rect.colliderect(stone.rect):
                dx = self.hero.rect.centerx - stone.rect.centerx
                dy = self.hero.rect.centery - stone.rect.centery

                # Normalize direction
                if dx == 0 and dy == 0:
                    dx, dy = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
                else:
                    length = max((dx**2 + dy**2)**0.5, 1)
                    dx /= length
                    dy /= length

                # Knockback vector (100 pixels)
                knockback_distance = 1
                knockback_x = int(dx * knockback_distance)
                knockback_y = int(dy * knockback_distance)

                # Apply knockback
                self.hero.rect.x += knockback_x
                self.hero.rect.y += knockback_y

                self.hero.update_position_from_rect()

                break

    # Function that displays a loading screen until stop_event is set
    def loading_screen(self, stop_event):
        spinner = itertools.cycle(["|", "/", "-", "\\"])
        background = pygame.image.load("assets/images/background.png")

        # Continue looping until stop_event is set
        while not stop_event.is_set():
            self.clock.tick(FPS)
            # Draw background
            self.screen.blit(background, (0, 0))

            # Build the loading message with spinner animation
            loading_text = "Loading " + next(spinner)
            # Render the loading text; adjust the size and color as needed
            text_surf = self.get_font(50).render(loading_text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(self.screen.get_width() // 2,
                                                   self.screen.get_height() // 2))
            self.screen.blit(text_surf, text_rect)

            # Update the display so that the text is visible
            pygame.display.flip()
            time.sleep(0.1)

    # Main function that sets up the multiprocessing processes
    def run_generate_with_loading(self):
        stop_event = multiprocessing.Event()
        result_queue = multiprocessing.Queue()

        # Start the process for generating questions
        generator_process = multiprocessing.Process(
            target=run_generate_question,
            args=(TOPIC, NUM_MONSTERS, stop_event, result_queue)
        )
        generator_process.start()

        # Show the loading screen in the main process while the generator runs
        self.loading_screen(stop_event)

        # Wait for the generator process to finish
        generator_process.join()

        # Retrieve and return the result from the queue
        result = result_queue.get()
        return result
