# src/utils.py
import math
import random
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



def get_valid_spawn_positions(x_min=100, x_max=int(0.8*WIDTH), y_min=100, y_max=int(0.8*HEIGHT)):
    """
    Returns a list of (x, y) positions inside the allowed area,
    aligned to the TILE_SIZE grid.
    """
    positions = []
    for x in range(x_min, x_max + 1, TILE_SIZE):
        for y in range(y_min, y_max + 1, TILE_SIZE):
            positions.append((x, y))
    return positions

def get_random_spawn_positions(count, exclude=[]):
    """
    Returns `count` random positions from valid area, excluding any in `exclude`.
    """
    positions = get_valid_spawn_positions()
    positions = [pos for pos in positions if pos not in exclude]
    return random.sample(positions, count)

def get_random_grid_position(exclude=[]):
    positions = [(x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT) if (x, y) not in exclude]
    return random.choice(positions)
