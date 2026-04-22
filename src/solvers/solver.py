from abc import ABC, abstractmethod
import csv
import inspect
import tracemalloc
import time
from pathlib import Path
from typing import Any, Dict, Optional

CSV_FILE_NAME = "solved.csv"
CSV_FIELDNAMES = ["input_file", "solver", "solved", "time", "node_expanded", "memory"]
PROJECT_ROOT = Path(__file__).resolve().parents[2]

MAX_NODES_DEFAULT = 10000000
MAX_NODES_BRUTE_FORCE = 100000
MAX_NODES_BACKTRACKING = 3000000
MAX_NODES_BACKWARD_CHAINING = 1500000
MAX_NODES_FORWARD_CHAINING = 5000000
MAX_NODES_ASTAR = 5000000


class Solver(ABC):
    """
    Base class for all solvers.

    Mục tiêu:
    - Định nghĩa interface chung.
    - Mọi class con trong solvers đều phải kế thừa và implement hàm solve.
    """

    def __init__(self, name: Optional[str] = None):
        self.name = name or self.__class__.__name__
        self.max_nodes = MAX_NODES_DEFAULT
        self.input_file: Optional[str] = None

        # metrics
        self.execution_time: float = 0.0
        self.node_expanded: int = 0
        self.memory_used: Optional[float] = None
        self.stop_reason: Optional[str] = None

    def run(self, *args, input_file: Optional[str] = None, output_file: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Wrapper cho mọi solver.
        """
        print(f"{self.name} is Solving ...")

        self.reset_metrics()
        self.input_file = input_file
        tracemalloc.start()
        start_time = time.perf_counter()

        solve_signature = inspect.signature(self.solve)
        params = solve_signature.parameters.values()
        accepts_output_file = (
            "output_file" in solve_signature.parameters
            or any(param.kind == inspect.Parameter.VAR_KEYWORD for param in params)
        )

        if accepts_output_file:
            solution = self.solve(*args, output_file=output_file, **kwargs)
        else:
            solution = self.solve(*args, **kwargs)

        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        self.execution_time = end_time - start_time
        self.memory_used = peak / 1024 / 1024  # MB

        metrics = {
            "input_file": self.input_file or "",
            "solver": self.name,
            "solved": solution is not None,
            "time": self.execution_time,
            "node_expanded": self.node_expanded,
            "memory": self.memory_used,
        }

        self._append_metrics_to_csv(metrics)

        print(f"{self.name} Done")
        return {
            "solver": self.name,
            "solution": solution,
            "time": self.execution_time,
            "node_expanded": self.node_expanded,
            "memory": self.memory_used,
            "stop_reason": self.stop_reason,
        }

    def _append_metrics_to_csv(self, metrics: Dict[str, Any]) -> None:
        file_path = PROJECT_ROOT / CSV_FILE_NAME
        write_header = not file_path.exists()
        with file_path.open("a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELDNAMES)
            if write_header:
                writer.writeheader()
            writer.writerow({key: metrics.get(key) for key in CSV_FIELDNAMES})

    # TODO: các thuật toán solver khác phải implement hàm này
    @abstractmethod
    def solve(self, puzzle):
        """
        Method chính để các solver implement.

        Input:
            puzzle (domain.Puzzle) (sẽ refactor project sau)
        Output:
            - trạng thái solved (grid)
            - hoặc None nếu không giải được
        """
        pass

    def reset_metrics(self):
        """Reset lại metrics trước mỗi lần chạy."""
        self.execution_time = 0
        self.node_expanded = 0
        self.memory_used = None
        self.stop_reason = None

    def has_exceeded_max_nodes(self) -> bool:
        return self.node_expanded > self.max_nodes

    def _mark_node_limit_reached(self) -> None:
        if self.stop_reason is not None:
            return
        self.stop_reason = f"Stopped: reached MAX_NODES={self.max_nodes}"
        print(f"[{self.name}] {self.stop_reason}")

    def increment_nodes(self, count: int = 1):
        """Dùng trong search algorithm."""
        self.node_expanded += count
        if self.has_exceeded_max_nodes():
            self._mark_node_limit_reached()

