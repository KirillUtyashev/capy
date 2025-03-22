import random

class Dungeon:
    def __init__(self, rows=60, cols=60, island_size=500):
        # rows and cols for the final grid (60x60) are determined by upscaling the 20x20 grid
        self.rows = rows
        self.cols = cols
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]
        self._generate_island(island_size)

    def _in_bounds(self, r, c, size):
        return 0 <= r < size and 0 <= c < size

    def _generate_island(self, target_size):
        # Step 1: Create a 20x20 base grid.
        base_size = 20
        base_grid = [[0 for _ in range(base_size)] for _ in range(base_size)]

        # Step 2: Create a guaranteed monotonic path from (0,0) to (base_size-1, base_size-1).
        base_grid[0][0] = 1
        # To reach from 0 to base_size-1, we need (base_size-1) rights and (base_size-1) downs.
        moves = ['R'] * (base_size - 1) + ['D'] * (base_size - 1)
        random.shuffle(moves)
        r, c = 0, 0
        for move in moves:
            if move == 'R':
                c += 1
            else:  # move == 'D'
                r += 1
            base_grid[r][c] = 1

        # Step 3: Expand the path.
        # For each cell that is 0, count how many cardinal neighbors are 1.
        # - If one neighbor is 1, chance of turning this cell to 1 is 40%.
        # - If two or more neighbors are 1, chance is 60%.
        expanded_grid = [row[:] for row in base_grid]  # work on a copy
        for r in range(base_size):
            for c in range(base_size):
                if base_grid[r][c] == 0:
                    count = 0
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = r + dr, c + dc
                        if self._in_bounds(nr, nc, base_size) and base_grid[nr][nc] == 1:
                            count += 1
                    chance = 0.0
                    if count >= 2:
                        chance = 0.6
                    elif count == 1:
                        chance = 0.4
                    if random.random() < chance:
                        expanded_grid[r][c] = 1
        base_grid = expanded_grid

        # Optionally, you can enforce a minimum number of 1's if desired, by checking against target_size.
        # For now, we assume target_size is used to control overall island "density" indirectly.

        # Step 4: Upscale the 20x20 grid to a 60x60 grid.
        # Each cell in the base grid becomes a 3x3 block in the final grid.
        upscale_factor = 3
        new_rows = base_size * upscale_factor  # should be 60
        new_cols = base_size * upscale_factor  # should be 60
        new_grid = [[0 for _ in range(new_cols)] for _ in range(new_rows)]
        for r in range(base_size):
            for c in range(base_size):
                if base_grid[r][c] == 1:
                    # Fill the corresponding 3x3 block with 1's.
                    for i in range(r * upscale_factor, r * upscale_factor + upscale_factor):
                        for j in range(c * upscale_factor, c * upscale_factor + upscale_factor):
                            new_grid[i][j] = 1

        self.grid = new_grid

    def get_grid(self):
        return self.grid

    def get_island_only(self):
        # Returns a grid with 1's for island cells and 0's for water.
        return [[1 if cell == 1 else 0 for cell in row] for row in self.grid]
