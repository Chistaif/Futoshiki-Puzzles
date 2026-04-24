"""AI solver worker manager for threaded solving and step streaming.

This module isolates threading, queues, and step-by-step solver event handling
from the GameScreen view code.
"""

from __future__ import annotations

import threading
from collections import deque
from queue import Empty, Queue
from typing import Any, Callable, Deque, Optional, Tuple

from src.domain.puzzle import PuzzleCase
from src.solvers.astar import AStarSolver
from src.solvers.backward import BackwardSolver
from src.solvers.backtrack import Backtracking
from src.solvers.brute_force import BruteForceSolver
from src.solvers.forward import ForwardSolver
from src.solvers.forward import ForwardSolver
from src.solvers.sat_solver import SATSolver
from src.file_io import write_output


StepHandler = Callable[[int, int, int], None]
StatusHandler = Callable[[str], None]
FinishHandler = Callable[[bool, Optional[str]], None]


class AISolverManager:
    """Manage AI solver worker thread and animation step queue."""

    def __init__(self, step_delay_ms: int = 75) -> None:
        self.pending_steps: Deque[Tuple[int, int, int]] = deque()
        self.step_delay_ms = step_delay_ms
        self.step_interval = self.step_delay_ms / 1000.0
        self.step_elapsed = 0.0

        self.animating = False
        self.solver_running = False
        self.solver_done = False
        self.solver_found_solution = False
        self.solver_stop_reason: Optional[str] = None

        self.solver_name = ""
        self.solver_key = "backtracking"

        self.worker_thread: Optional[threading.Thread] = None
        self.worker_cancel_event = threading.Event()
        self.event_queue: Queue[Tuple[str, Any]] = Queue()

    def reset(self, wait_timeout: float = 0.15) -> None:
        self._stop_ai_worker(wait_timeout)
        self.pending_steps = deque()
        self.step_elapsed = 0.0
        self.animating = False
        self.solver_running = False
        self.solver_done = False
        self.solver_found_solution = False
        self.solver_stop_reason = None
        self.solver_name = ""
        self.event_queue = Queue()

    def shutdown(self) -> None:
        self._stop_ai_worker(wait_timeout=0.25)

    def start(self, case: PuzzleCase, solver_name: str) -> None:
        normalized_solver = str(solver_name).strip().lower()
        if normalized_solver in ("a*", "a_star"):
            normalized_solver = "astar"
        elif normalized_solver in ("bruteforce", "brute-force", "brute force"):
            normalized_solver = "brute_force"
        elif normalized_solver in ("backward_chaining", "backward_solver"):
            normalized_solver = "backward"
        elif normalized_solver in ("forward_chaining", "dpll", "forward_solver"):
            normalized_solver = "forward"
        elif normalized_solver in ("sat", "sat_solver", "pysat"):
            normalized_solver = "sat"

        if normalized_solver not in ("backtracking", "brute_force", "backward", "forward", "astar", "sat"):
            raise ValueError(f"Unsupported solver: {solver_name}")

        self.pending_steps = deque()
        self.step_elapsed = 0.0
        self.solver_done = False
        self.solver_found_solution = False
        self.solver_stop_reason = None
        self.solver_running = True
        self.animating = True
        self.solver_key = normalized_solver
        solver_display_names = {
            "backtracking": "Backtracking",
            "brute_force": "Brute Force",
            "backward": "Backward Chaining",
            "forward": "Forward Chaining",
            "astar": "A* Search",
            "sat": "SAT Solver",
        }
        self.solver_name = solver_display_names[normalized_solver]

        self._start_ai_worker(case, normalized_solver)

    def update(
        self,
        dt: float,
        apply_step: StepHandler,
        set_status: StatusHandler,
        on_finished: FinishHandler,
    ) -> None:
        self._drain_ai_events(set_status)

        if not self.animating:
            return

        self.step_elapsed += dt
        while self.step_elapsed >= self.step_interval and self.animating:
            self.step_elapsed -= self.step_interval
            self._apply_next_ai_step(apply_step, set_status)

        if not self.pending_steps and self.solver_done:
            self.animating = False
            on_finished(self.solver_found_solution, self.solver_stop_reason)

    def _start_ai_worker(self, case: PuzzleCase, solver_name: str) -> None:
        self._stop_ai_worker(wait_timeout=0.05)
        event_queue: Queue[Tuple[str, Any]] = Queue()
        cancel_event = threading.Event()
        self.event_queue = event_queue
        self.worker_cancel_event = cancel_event

        worker = threading.Thread(
            target=self._run_solver_worker,
            args=(case, solver_name, event_queue, cancel_event),
            daemon=True,
        )
        self.worker_thread = worker
        worker.start()

    def _run_solver_worker(
        self,
        case: PuzzleCase,
        solver_name: str,
        event_queue: Queue[Tuple[str, Any]],
        cancel_event: threading.Event,
    ) -> None:
        try:
            input_file = case.name
            output_file = input_file.replace("input", "output")

            if not output_file.endswith(".txt"):
                output_file += ".txt"

            def on_step(row: int, col: int, value: int) -> None:
                if cancel_event.is_set():
                    raise RuntimeError("solver-cancelled")
                event_queue.put(("step", (row, col, value)))

            if solver_name == "astar":
                solver = AStarSolver(case, use_ac3=True, emit_search_trace=True)
                result = solver.run(step_callback=on_step, input_file=input_file, output_file = output_file)
            elif solver_name == "brute_force":
                solver = BruteForceSolver(case)
                result = solver.run(step_callback=on_step, input_file=input_file, output_file = output_file)
            elif solver_name == "sat":
                solver = SATSolver(case)
                result = solver.run(step_callback=on_step, input_file=input_file)
            elif solver_name == "backward":
                solver = BackwardSolver()
                result = solver.run(case, step_callback=on_step, input_file=input_file, output_file = output_file)
            elif solver_name == "forward":
                # Chỉ giữ lại một lần khởi tạo và chạy duy nhất
                solver = ForwardSolver()
                result = solver.run(case, step_callback=on_step, input_file=input_file, output_file=output_file)
            else:
                solver = Backtracking(case)
                result = solver.run(step_callback=on_step, input_file=input_file, output_file = output_file)

            solved_grid = result.get("solution")
            stop_reason = result.get("stop_reason")

            if solved_grid:
                write_output(case.n, solved_grid, case.horizontal, case.vertical, output_file)

            if cancel_event.is_set():
                event_queue.put(("cancelled", None))
                return

            event_queue.put(("done", {"found_solution": solved_grid is not None, "stop_reason": stop_reason}))
        except RuntimeError as exc:
            if str(exc) == "solver-cancelled":
                event_queue.put(("cancelled", None))
                return
            event_queue.put(("error", str(exc)))
        except Exception as exc:  # pragma: no cover
            event_queue.put(("error", str(exc)))

    def _stop_ai_worker(self, wait_timeout: float) -> None:
        self.worker_cancel_event.set()
        worker = self.worker_thread
        if worker is not None and worker.is_alive():
            worker.join(timeout=wait_timeout)
        self.worker_thread = None

    def _drain_ai_events(self, set_status: StatusHandler) -> None:
        while True:
            try:
                event_type, payload = self.event_queue.get_nowait()
            except Empty:
                break

            if event_type == "step":
                row, col, value = payload
                self.pending_steps.append((row, col, value))
                continue

            if event_type == "done":
                self.solver_running = False
                self.solver_done = True
                if isinstance(payload, dict):
                    self.solver_found_solution = bool(payload.get("found_solution", False))
                    stop_reason = payload.get("stop_reason")
                    self.solver_stop_reason = str(stop_reason) if stop_reason else None
                else:
                    self.solver_found_solution = bool(payload)
                    self.solver_stop_reason = None
                continue

            if event_type == "cancelled":
                self.solver_running = False
                self.solver_done = True
                self.solver_found_solution = False
                self.solver_stop_reason = None
                self.pending_steps = deque()
                self.animating = False
                set_status("Solver cancelled")
                continue

            if event_type == "error":
                self.solver_running = False
                self.solver_done = True
                self.solver_found_solution = False
                self.solver_stop_reason = None
                self.pending_steps = deque()
                self.animating = False
                set_status(f"Solver error: {payload}")

    def _apply_next_ai_step(self, apply_step: StepHandler, set_status: StatusHandler) -> None:
        if not self.pending_steps:
            return

        row, col, value = self.pending_steps.popleft()
        apply_step(row, col, value)

        if value != 0:
            set_status(f"Thinking ({self.solver_name})...")
            return

        if self.solver_key == "backtracking":
            set_status("Backtracking...")
        else:
            set_status(f"Thinking ({self.solver_name})...")

