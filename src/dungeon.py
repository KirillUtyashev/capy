import random

class Dungeon:
    def __init__(self, rows=60, cols=60, island_size=500):
        self.rows = rows
        self.cols = cols
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]
        self._generate_island(island_size)

    def _in_bounds(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols

    def _generate_island(self, target_size):
        start_r, start_c = 0, 0
        queue = [(start_r, start_c)]
        visited = set()

        while queue and len(visited) < target_size:
            r, c = queue.pop(0)
            if not self._in_bounds(r, c) or (r, c) in visited:
                continue

            visited.add((r, c))
            self.grid[r][c] = 1

            # Add random neighbors
            directions = [(-1,0), (1,0), (0,-1), (0,1)]
            random.shuffle(directions)
            for dr, dc in directions:
                if random.random() < 0.9:  # randomness = organic shape
                    nr, nc = r + dr, c + dc
                    if self._in_bounds(nr, nc) and (nr, nc) not in visited:
                        queue.append((nr, nc))

    def get_grid(self):
        return self.grid

    def get_island_only(self):
        return [[1 if cell == 1 else 0 for cell in row] for row in self.grid]
