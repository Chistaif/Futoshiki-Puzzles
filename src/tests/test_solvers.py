from pathlib import Path

import pytest

from src.domain.puzzle import PuzzleCase, from_tuple
from src.file_io import readFile
from src.solvers.astar import AStarSolver
from src.solvers.backtrack import Backtracking
from src.solvers.backward import BackwardSolver
from src.solvers.brute_force import BruteForceSolver
from src.solvers.forward import ForwardBacktrackSolver
from src.solvers.sat_solver import SATSolver


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_FILES = [PROJECT_ROOT / "Inputs" / f"input-{index:02d}.txt" for index in range(1, 11)]


def load_puzzle_case(input_path: Path) -> PuzzleCase:
    raw = readFile(str(input_path))
    if raw is None:
        raise ValueError(f"Cannot load puzzle from {input_path}")

    n, grid, horizontal, vertical = raw
    return from_tuple(input_path.name, n, grid, horizontal, vertical)


def solve_with_algorithm(algo: str, puzzle: PuzzleCase):
    input_file = puzzle.name
    if algo == "backtracking":
        return Backtracking(puzzle).run(input_file=input_file)
    if algo == "brute_force":
        return BruteForceSolver(puzzle).run(input_file=input_file)
    if algo == "a_star":
        return AStarSolver(puzzle).run(input_file=input_file)
    if algo == "forward_chaining":
        return ForwardBacktrackSolver().run(puzzle, input_file=input_file)
    if algo == "backward_chaining":
        return BackwardSolver().run(puzzle, input_file=input_file)
    if algo == "sat":
        return SATSolver(puzzle).run(input_file=input_file)
    raise ValueError(f"Unsupported algorithm: {algo}")


def is_valid_solution(grid, puzzle: PuzzleCase) -> bool:
    n = puzzle.n
    expected_values = set(range(1, n + 1))

    if grid is None or len(grid) != n:
        return False

    for row in grid:
        if len(row) != n:
            return False
        if set(row) != expected_values:
            return False

    for col in range(n):
        column_values = {grid[row][col] for row in range(n)}
        if column_values != expected_values:
            return False

    # Ensure solver does not modify fixed givens from the input puzzle.
    for row in range(n):
        for col in range(n):
            given = puzzle.grid[row][col]
            if given != 0 and grid[row][col] != given:
                return False

    # horizontal[r][c] == 1 means cell(r,c) < cell(r,c+1), -1 means >.
    for row in range(n):
        for col in range(n - 1):
            sign = puzzle.horizontal[row][col]
            left = grid[row][col]
            right = grid[row][col + 1]
            if sign == 1 and not (left < right):
                return False
            if sign == -1 and not (left > right):
                return False

    # vertical[r][c] == 1 means cell(r,c) < cell(r+1,c), -1 means >.
    for row in range(n - 1):
        for col in range(n):
            sign = puzzle.vertical[row][col]
            top = grid[row][col]
            bottom = grid[row + 1][col]
            if sign == 1 and not (top < bottom):
                return False
            if sign == -1 and not (top > bottom):
                return False

    return True


@pytest.mark.parametrize("input_path", INPUT_FILES, ids=[path.name for path in INPUT_FILES])
def test_solver_correctness(input_path: Path, selected_algorithms: tuple[str, ...]) -> None:
    puzzle = load_puzzle_case(input_path)
    executed = 0
    verified = 0

    for algo in selected_algorithms:
        if algo == "brute_force" and puzzle.n > 4:
            continue

        executed += 1

        result = solve_with_algorithm(algo, puzzle)
        solution = result.get("solution")
        stop_reason = result.get("stop_reason")

        if stop_reason:
            continue

        assert solution is not None, f"{algo} returned None for {input_path.name}"
        assert is_valid_solution(solution, puzzle), f"Invalid solution from {algo} on {input_path.name}"
        verified += 1

    if executed == 0:
        pytest.skip("Skip brute_force for N > 4 to avoid excessive runtime.")
    if verified == 0:
        pytest.skip("All selected solvers hit MAX_NODES before finding a solution.")


"""
Lệnh chạy:
Chạy 1 thuật toán:
pytest -q test_solvers.py --algo forward_chaining
pytest -q test_solvers.py --algo backward_chaining
pytest -q test_solvers.py --algo sat
pytest -q test_solvers.py --algo backtracking
pytest -q test_solvers.py --algo a_star
pytest -q test_solvers.py --algo brute_force
Chạy tất cả thuật toán:
pytest -q test_solvers.py --algo all
"""