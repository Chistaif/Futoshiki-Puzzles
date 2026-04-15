from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import time

class Solver(ABC):
    """
    Base class for all solvers.

    Mục tiêu:
    - Định nghĩa interface chung
    - Mọi class con trong solvers đều phải kế thừa và implement hàm solve
    """
    def __init__(self, name: Optional[str] = None):
        self.name = name or self.__class__.__name__

        # metrics
        self.execution_time: float = 0.0
        self.node_expanded: int = 0
        self.memory_used: Optional[float] = None

    def run(self, puzzle) -> Dict[str, Any]:
        """
        Wrapper cho mọi solver
        """
        start_time = time.perf_counter()
        solution = self.solve(puzzle)
        end_time = time.perf_counter()

        self.execution_time = end_time - start_time

        return {
            "solver": self.name,
            "solution": solution,
            "time": self.execution_time,
            "node_expanded": self.node_expanded,
            "memory":    self.memory_used,
        }

    # TODO: các thuật toán solver khác phải implement hàm này
    @abstractmethod
    def solve(self, puzzle):
        """
        Method chính để các solver implement

        Input:
            puzzle (domain.Puzzle) (sẽ refactor project sau)
        Output:
            - trạng thái solved (grid)
            - hoạc None nếu k giải đc thì
        """
        pass

    def reset_metrics(self):
        """Reset lại metrics trước mỗi lần chạy"""
        self.execution_time = 0
        self.node_expanded = 0
        self.memory_used = None

    def increment_nodes(self, count: int = 1):
        """Dùng trong search algorithm"""
        self.nodes_expanded += count