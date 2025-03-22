# src/utils.py
import math
import random
import pygame
from .settings import TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, WIDTH, HEIGHT
def reposition_hero(hero, monster, distance=100):
    """
    Move 'hero' so its center is 'distance' pixels away
    from 'monster's center, preventing immediate re-collision.
    """
    dx = hero.rect.centerx - monster.rect.centerx
    dy = hero.rect.centery - monster.rect.centery

    # If they overlap exactly, just shift hero horizontally by 'distance'.
    if dx == 0 and dy == 0:
        hero.rect.x += distance
        return

    length = math.sqrt(dx * dx + dy * dy)
    scale = distance / length

    new_x = monster.rect.centerx + dx * scale
    new_y = monster.rect.centery + dy * scale

    hero.rect.centerx = int(new_x)
    hero.rect.centery = int(new_y)



def get_valid_spawn_positions(dungeon, tile_size=TILE_SIZE):
    """
    Returns a list of (x, y) positions for valid spawn locations inside the dungeon,
    aligned to the tile_size grid.

    Parameters:
    - dungeon: an instance of the Dungeon class.
    - tile_size: size of each tile in pixels.

    Returns:
    - A list of tuples (x, y) for every island cell in the dungeon's grid.
    """
    grid = dungeon.get_island_only()  # grid with 1's for island cells, 0's for water
    positions = []
    for row_idx, row in enumerate(grid):
        for col_idx, cell in enumerate(row):
            if cell == 1:  # valid spawn position (island cell)
                x = col_idx * tile_size
                y = row_idx * tile_size
                positions.append((x, y))
    return positions

def get_random_spawn_positions(dungeon, count, exclude=None, tile_size=TILE_SIZE):
    """
    Returns `count` random spawn positions from valid locations inside the dungeon,
    excluding any positions provided in `exclude`.

    Parameters:
    - dungeon: an instance of the Dungeon class.
    - count: number of random spawn positions to return.
    - exclude: a list of (x, y) positions to exclude from the selection.
    - tile_size: size of each tile in pixels.

    Returns:
    - A list of `count` randomly selected (x, y) positions from valid island cells.
    """
    if exclude is None:
        exclude = []
    positions = get_valid_spawn_positions(dungeon, tile_size)
    # Filter out positions that are in the exclude list
    positions = [pos for pos in positions if pos not in exclude]
    return random.sample(positions, count)

def get_random_grid_position(exclude=[]):
    positions = [(x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT) if (x, y) not in exclude]
    return random.choice(positions)

def tint_image(image, tint_color):
    """Return a tinted copy of the given image."""
    tinted_image = image.copy()
    tinted_image.fill(tint_color, special_flags=pygame.BLEND_RGB_ADD)
    return tinted_image
