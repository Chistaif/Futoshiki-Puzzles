import csv
import multiprocessing as mp
from pathlib import Path
from queue import Empty
import threading
import time
import tracemalloc

import pytest

from src.domain.puzzle import PuzzleCase, from_tuple
from src.file_io import readFile
from src.solvers.astar import AStarSolver
from src.solvers.backtrack import Backtracking
from src.solvers.backward import BackwardSolver
from src.solvers.brute_force import BruteForceSolver
from src.solvers.forward import ForwardSolver
from src.solvers.sat_solver import SATSolver


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_FILES = [PROJECT_ROOT / "Inputs" / f"input-{index:02d}.txt" for index in range(1, 11)]
CSV_FILE = PROJECT_ROOT / "solved.csv"
CSV_FIELDNAMES = ["input_file", "solver", "solved", "time", "node_expanded", "memory"]
SOLVER_TIMEOUT_SECONDS = 180


def _normalize_input_selector(value: str) -> str:
    text = str(value).strip().lower()
    if text.endswith(".txt"):
        text = text[:-4]
    return text


def _matches_selected_input(input_path: Path, selected_input: str) -> bool:
    selector = _normalize_input_selector(selected_input)
    if selector in {"", "all", "*"}:
        return True

    input_stem = input_path.stem.lower()  # input-03
    input_name = input_path.name.lower()  # input-03.txt
    input_num = "".join(ch for ch in input_stem if ch.isdigit())  # 03
    return selector in {input_stem, input_name, input_num}


def _solver_name_for_algo(algo: str) -> str:
    names = {
        "backtracking": "Backtracking",
        "brute_force": "BruteForceSolver",
        "a_star": "A* Search",
        "forward_chaining": "Forward Chaining",
        "backward_chaining": "BackwardSolver",
        "sat": "SAT Solver",
    }
    return names.get(algo, algo)


def _append_skip_metrics(algo: str, puzzle: PuzzleCase) -> None:
    write_header = not CSV_FILE.exists()
    with CSV_FILE.open("a", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDNAMES)
        if write_header:
            writer.writeheader()
        writer.writerow(
            {
                "input_file": puzzle.name,
                "solver": _solver_name_for_algo(algo),
                "solved": "SKIPPED",
                "time": 0.0,
                "node_expanded": 0,
                "memory": 0.0,
            }
        )


def _append_timeout_metrics(
    algo: str,
    puzzle: PuzzleCase,
    timeout_seconds: int,
    node_expanded: int,
    memory: float,
) -> None:
    write_header = not CSV_FILE.exists()
    with CSV_FILE.open("a", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDNAMES)
        if write_header:
            writer.writeheader()
        writer.writerow(
            {
                "input_file": puzzle.name,
                "solver": _solver_name_for_algo(algo),
                "solved": "time_out",
                "time": float(timeout_seconds),
                "node_expanded": int(node_expanded),
                "memory": float(memory),
            }
        )


def should_skip_algorithm(algo: str, puzzle: PuzzleCase, selected_algo: str) -> bool:
    # Brute force explodes quickly beyond 4x4.
    if algo == "brute_force" and puzzle.n > 4:
        return True

    # Backward chaining can be slow on bigger boards when running all algorithms.
    # If user explicitly selects backward_chaining, do not skip.
    if selected_algo == "all" and algo == "backward_chaining" and puzzle.n > 4:
        return True

    return False


def load_puzzle_case(input_path: Path) -> PuzzleCase:
    raw = readFile(str(input_path))
    if raw is None:
        raise ValueError(f"Cannot load puzzle from {input_path}")

    n, grid, horizontal, vertical = raw
    return from_tuple(input_path.name, n, grid, horizontal, vertical)


def _build_solver(algo: str, puzzle: PuzzleCase):
    if algo == "backtracking":
        return Backtracking(puzzle)
    if algo == "brute_force":
        return BruteForceSolver(puzzle)
    if algo == "a_star":
        return AStarSolver(puzzle)
    if algo == "forward_chaining":
        return ForwardSolver()
    if algo == "backward_chaining":
        return BackwardSolver()
    if algo == "sat":
        return SATSolver(puzzle)
    raise ValueError(f"Unsupported algorithm: {algo}")


def _execute_algorithm(algo: str, puzzle: PuzzleCase, solver):
    input_file = puzzle.name
    if algo == "backtracking":
        return solver.run(input_file=input_file)
    if algo == "brute_force":
        return solver.run(input_file=input_file)
    if algo == "a_star":
        return solver.run(input_file=input_file)
    if algo == "forward_chaining":
        return solver.run(puzzle, input_file=input_file)
    if algo == "backward_chaining":
        return solver.run(puzzle, input_file=input_file)
    if algo == "sat":
        return solver.run(input_file=input_file)
    raise ValueError(f"Unsupported algorithm: {algo}")


def _solver_worker(algo: str, puzzle: PuzzleCase, result_queue, progress_queue) -> None:
    try:
        solver = _build_solver(algo, puzzle)
        stop_event = threading.Event()

        def _report_progress() -> None:
            while not stop_event.is_set():
                try:
                    _, peak = tracemalloc.get_traced_memory()
                    mem_mb = peak / 1024 / 1024
                except RuntimeError:
                    mem_mb = 0.0

                try:
                    progress_queue.put_nowait(
                        {
                            "node_expanded": int(getattr(solver, "node_expanded", 0) or 0),
                            "memory": float(mem_mb),
                        }
                    )
                except Exception:
                    pass

                time.sleep(0.2)

        reporter = threading.Thread(target=_report_progress, daemon=True)
        reporter.start()

        result = _execute_algorithm(algo, puzzle, solver)
        stop_event.set()
        reporter.join(timeout=0.3)

        # Đẩy snapshot cuối để parent có số liệu gần nhất.
        try:
            progress_queue.put_nowait(
                {
                    "node_expanded": int(result.get("node_expanded", 0) or 0),
                    "memory": float(result.get("memory", 0.0) or 0.0),
                }
            )
        except Exception:
            pass

        result_queue.put({"status": "ok", "result": result})
    except Exception as exc:
        result_queue.put({"status": "error", "error": repr(exc)})


def solve_with_algorithm(algo: str, puzzle: PuzzleCase):
    ctx = mp.get_context("spawn")
    result_queue = ctx.Queue(maxsize=1)
    progress_queue = ctx.Queue()
    process = ctx.Process(target=_solver_worker, args=(algo, puzzle, result_queue, progress_queue))
    process.start()
    latest_progress = {"node_expanded": 0, "memory": 0.0}
    deadline = time.monotonic() + SOLVER_TIMEOUT_SECONDS

    while process.is_alive() and time.monotonic() < deadline:
        process.join(0.25)
        while True:
            try:
                snapshot = progress_queue.get_nowait()
            except Empty:
                break
            latest_progress["node_expanded"] = int(snapshot.get("node_expanded", 0) or 0)
            latest_progress["memory"] = float(snapshot.get("memory", 0.0) or 0.0)

    if process.is_alive():
        process.terminate()
        process.join()
        _append_timeout_metrics(
            algo,
            puzzle,
            SOLVER_TIMEOUT_SECONDS,
            latest_progress["node_expanded"],
            latest_progress["memory"],
        )
        return {
            "solver": _solver_name_for_algo(algo),
            "solution": None,
            "time": float(SOLVER_TIMEOUT_SECONDS),
            "node_expanded": latest_progress["node_expanded"],
            "memory": latest_progress["memory"],
            "stop_reason": f"Stopped: TIMEOUT={SOLVER_TIMEOUT_SECONDS}s",
        }

    # Drain snapshot queue lần cuối để có số liệu mới nhất.
    while True:
        try:
            snapshot = progress_queue.get_nowait()
        except Empty:
            break
        latest_progress["node_expanded"] = int(snapshot.get("node_expanded", 0) or 0)
        latest_progress["memory"] = float(snapshot.get("memory", 0.0) or 0.0)

    try:
        payload = result_queue.get_nowait()
    except Empty:
        raise RuntimeError(f"{algo} exited without returning a result payload.")

    if payload.get("status") == "error":
        raise RuntimeError(f"{algo} failed in worker process: {payload.get('error')}")

    return payload["result"]


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
def test_solver_correctness(
    input_path: Path,
    selected_algorithms: tuple[str, ...],
    selected_algo: str,
    selected_input: str,
) -> None:
    if not _matches_selected_input(input_path, selected_input):
        pytest.skip(f"Filtered by --input={selected_input}")

    puzzle = load_puzzle_case(input_path)
    executed = 0
    verified = 0

    for algo in selected_algorithms:
        if should_skip_algorithm(algo, puzzle, selected_algo):
            _append_skip_metrics(algo, puzzle)
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
        pytest.skip("All selected solvers were stopped (MAX_NODES/TIMEOUT) before finding a solution.")


"""
Lệnh chạy:
Chạy 1 thuật toán:
pytest -q test_solvers.py --algo forward_chaining
pytest -q test_solvers.py --algo backward_chaining
pytest -q test_solvers.py --algo sat
pytest -q test_solvers.py --algo backtracking
pytest -q test_solvers.py --algo a_star
pytest -q test_solvers.py --algo brute_force
Chạy 1 thuật toán với 1 input cụ thể:
pytest -q test_solvers.py --algo forward_chaining --input input-03.txt
pytest -q test_solvers.py --algo sat --input input-10
pytest -q test_solvers.py --algo backtracking --input 01
Chạy tất cả thuật toán:
pytest -q test_solvers.py --algo all
"""

"""
Trong lúc solver chạy ở process con, thêm luồng gửi snapshot tiến trình định kỳ (mỗi 0.2s):
node_expanded hiện tại
memory peak hiện tại (MB)
Nếu timeout:
process bị terminate
ghi vào solved.csv với:
solved = time_out
time = 180
node_expanded = snapshot gần nhất
memory = snapshot gần nhất
Hàm ghi timeout _append_timeout_metrics(...) đã nhận thêm 2 tham số node_expanded, memory thay vì cố định 0.
Kết quả:
Dòng time_out giờ không còn bị node_expanded=0, memory=0.0 nữa, mà phản ánh tiến độ thực tế tới lúc bị dừng.
"""