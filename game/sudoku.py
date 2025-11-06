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

    # Row
    if num in grid[r]:
        return False

    # Column
    if num in [grid[i][c] for i in range(GRID_SIZE)]:
        return False

    # Subgrid
    sub_x = (c // SUBGRID_SIZE) * SUBGRID_SIZE
    sub_y = (r // SUBGRID_SIZE) * SUBGRID_SIZE

    for i in range(sub_y, sub_y + SUBGRID_SIZE):
        for j in range(sub_x, sub_x + SUBGRID_SIZE):
            if grid[i][j] == num:
                return False

    return True


def solve(grid):
    """Backtracking Sudoku solver."""
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


def fill_grid(grid):
    """Fills grid completely with a valid Sudoku solution."""
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


def count_solutions(grid):
    """Count number of valid Sudoku solutions (used to ensure uniqueness)."""
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
    """
    Remove numbers while keeping unique solution.
    remove_count = number of cells to attempt clearing.
    """
    attempts = remove_count
    while attempts > 0:
        row = random.randint(0, 8)
        col = random.randint(0, 8)

        if grid[row][col] == 0:
            continue

        backup = grid[row][col]
        grid[row][col] = 0

        # Ensure the puzzle still has a unique solution
        grid_copy = copy.deepcopy(grid)
        solutions = count_solutions(grid_copy)

        if solutions != 1:
            grid[row][col] = backup  # Restore if not unique
        attempts -= 1

    return grid


def generate_sudoku(difficulty="medium", seed=None):
    """
    Generate a Sudoku puzzle and its solution.
    difficulty: 'easy', 'medium', 'hard'
    seed: optional random seed (for reproducible puzzles)
    Returns (puzzle, solution)
    """
    if seed is not None:
        random.seed(seed)

    difficulty_map = {
        "easy": 38,
        "medium": 48,
        "hard": 56,
    }

    remove_count = difficulty_map.get(difficulty.lower(), 48)

    # Step 1: Fill a full valid Sudoku grid
    grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    fill_grid(grid)

    # Step 2: Copy solution
    solution = copy.deepcopy(grid)

    # Step 3: Remove numbers to create puzzle
    puzzle = remove_numbers(grid, remove_count)

    return puzzle, solution


# Example test run
if __name__ == "__main__":
    for level in ["easy", "medium", "hard"]:
        print(f"\n=== {level.upper()} ===")
        puzzle, solution = generate_sudoku(level)
        for row in puzzle:
            print(row)
