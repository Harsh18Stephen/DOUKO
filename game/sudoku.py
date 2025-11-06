import random
import copy

GRID_SIZE = 9
SUBGRID_SIZE = 3


def find_empty(grid):
    """Finds the next empty cell (0 = empty)."""
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if grid[r][c] == 0:
                return r, c
    return None


def valid(grid, num, pos):
    """Checks if num can be placed at pos (row, col)."""
    r, c = pos

    if num in grid[r]:
        return False

    if num in [grid[i][c] for i in range(GRID_SIZE)]:
        return False

    sub_x = (c // SUBGRID_SIZE) * SUBGRID_SIZE
    sub_y = (r // SUBGRID_SIZE) * SUBGRID_SIZE

    for i in range(sub_y, sub_y + SUBGRID_SIZE):
        for j in range(sub_x, sub_x + SUBGRID_SIZE):
            if grid[i][j] == num:
                return False

    return True


def solve(grid):
    # Backtracking
    find = find_empty(grid)
    if not find:
        return True
    else:
        r, c = find

    for num in range(1, 10):
        if valid(grid, num, (r, c)):
            grid[r][c] = num
            if solve(grid):
                return True
            grid[r][c] = 0

    return False

# Solution
def fill_grid(grid):
    find = find_empty(grid)
    if not find:
        return True
    else:
        r, c = find

    nums = list(range(1, 10))
    random.shuffle(nums)

    for num in nums:
        if valid(grid, num, (r, c)):
            grid[r][c] = num
            if fill_grid(grid):
                return True
            grid[r][c] = 0
    return False

# check unique 
def count_solutions(grid):
    find = find_empty(grid)
    if not find:
        return 1
    else:
        r, c = find

    count = 0
    for num in range(1, 10):
        if valid(grid, num, (r, c)):
            grid[r][c] = num
            count += count_solutions(grid)
            grid[r][c] = 0
            if count > 1:
                break
    return count


def remove_numbers(grid, remove_count):
    attempts = remove_count
    while attempts > 0:
        row = random.randint(0, 8)
        col = random.randint(0, 8)

        if grid[row][col] == 0:
            continue

        backup = grid[row][col]
        grid[row][col] = 0

        grid_copy = copy.deepcopy(grid)
        solutions = count_solutions(grid_copy)

        if solutions != 1:
            grid[row][col] = backup  
        attempts -= 1

    return grid


def generate_sudoku(difficulty="medium", seed=None):
    if seed is not None:
        random.seed(seed)

    difficulty_map = {
        "easy": 38,
        "medium": 48,
        "hard": 56,
    }

    remove_count = difficulty_map.get(difficulty.lower(), 48)

    grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    fill_grid(grid)

    solution = copy.deepcopy(grid)

    puzzle = remove_numbers(grid, remove_count)

    return puzzle, solution

# text
if __name__ == "__main__":
    for level in ["easy", "medium", "hard"]:
        print(f"\n=== {level.upper()} ===")
        puzzle, solution = generate_sudoku(level)
        for row in puzzle:
            print(row)
