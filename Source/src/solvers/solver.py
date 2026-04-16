from abc import ABC, abstractmethod
import tracemalloc
import time
from typing import Any, Dict, Optional


class Solver(ABC):
    """
    Base class for all solvers.

    Má»¥c tiÃªu:
    - Äá»‹nh nghÄ©a interface chung
    - Má»i class con trong solvers Ä‘á»u pháº£i káº¿ thá»«a vÃ  implement hÃ m solve
    """

    def __init__(self, name: Optional[str] = None):
        self.name = name or self.__class__.__name__

        # metrics
        self.execution_time: float = 0.0
        self.node_expanded: int = 0
        self.memory_used: Optional[float] = None

    def run(self, puzzle) -> Dict[str, Any]:
        """
        Wrapper cho má»i solver
        """
        print(f"{self.name} is Solving ...")

        tracemalloc.start()
        start_time = time.perf_counter()

        solution = self.solve(puzzle)

        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        self.execution_time = end_time - start_time
        self.memory_used = peak / 1024 / 1024  # MB

        print(f"{self.name} Done")
        return {
            "solver": self.name,
            "solution": solution,
            "time": self.execution_time,
            "node_expanded": self.node_expanded,
            "memory": self.memory_used,
        }

    # TODO: cÃ¡c thuáº­t toÃ¡n solver khÃ¡c pháº£i implement hÃ m nÃ y
    @abstractmethod
    def solve(self, puzzle):
        """
        Method chÃ­nh Ä‘á»ƒ cÃ¡c solver implement

        Input:
            puzzle (domain.Puzzle) (sáº½ refactor project sau)
        Output:
            - tráº¡ng thÃ¡i solved (grid)
            - hoáº¡c None náº¿u k giáº£i Ä‘c thÃ¬
        """
        pass

    def reset_metrics(self):
        """Reset láº¡i metrics trÆ°á»›c má»—i láº§n cháº¡y"""
        self.execution_time = 0
        self.node_expanded = 0
        self.memory_used = None

    def increment_nodes(self, count: int = 1):
        """DÃ¹ng trong search algorithm"""
        self.node_expanded += count

