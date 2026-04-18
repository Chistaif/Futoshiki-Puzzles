"""A* solver for Futoshiki puzzles.

This module keeps heuristic logic and state-space traversal separated so the
algorithm can be benchmarked against other solvers (for example Backtracking).
"""

from __future__ import annotations

import copy
import heapq
from collections import deque
from itertools import count
from typing import Callable, Deque, Dict, List, Optional, Set, Tuple

from src.domain.puzzle import PuzzleCase
from src.solvers.solver import Solver


StepCallback = Callable[[int, int, int], None]
Cell = Tuple[int, int]
State = Tuple[Tuple[int, ...], ...]
DomainMap = Dict[Cell, Set[int]]


class AStarSolver(Solver):
	"""Solve Futoshiki with A* + AC-3 heuristic.

	State definition:
	- A state is a partial assignment of the board.
	- 0 means unassigned.

	Cost model:
	- g(s): number of assignments made from the initial state.
	- h(s): number of unassigned cells U(s).
	  If AC-3 detects inconsistency (empty domain), h(s) = inf (dead state).
	- f(s) = g(s) + h(s).
	"""

	def __init__(
		self,
		puzzle: PuzzleCase,
		use_ac3: bool = True,
		emit_search_trace: bool = False,
	):
		super().__init__(name="A* Search")
		self.n = puzzle.n
		self.grid = copy.deepcopy(puzzle.grid)
		self.horizontal = puzzle.horizontal
		self.vertical = puzzle.vertical
		self.use_ac3 = use_ac3
		self.emit_search_trace = emit_search_trace

		self.givens: Dict[Cell, int] = {}
		for row in range(self.n):
			for col in range(self.n):
				value = self.grid[row][col]
				if value != 0:
					self.givens[(row, col)] = value

		self.cells: List[Cell] = [(row, col) for row in range(self.n) for col in range(self.n)]
		self.neighbors: Dict[Cell, Set[Cell]] = self._build_neighbors()
		self.initial_filled_cells = len(self.givens)

	def solve(self, step_callback: Optional[StepCallback] = None) -> Optional[List[List[int]]]:
		"""Return solved grid or None if no solution exists."""
		start_state = self._grid_to_state(self.grid)

		if not self._is_initial_state_valid(start_state):
			return None

		start_h, start_domains = self.evaluate_heuristic(start_state)
		if start_h == float("inf"):
			return None

		start_g = self._count_assignments_from_initial(start_state)
		pq: List[Tuple[float, float, int, int, State, DomainMap]] = []
		serial = count()
		heapq.heappush(
			pq,
			(start_g + start_h, start_h, -start_g, next(serial), start_state, start_domains),
		)

		parents: Dict[State, Tuple[State, Tuple[int, int, int]]] = {}
		best_g: Dict[State, int] = {start_state: start_g}
		closed: Set[State] = set()

		while pq:
			_, _, _, _, state, domains = heapq.heappop(pq)
			if state in closed:
				continue

			self.increment_nodes()
			closed.add(state)
			if self._is_goal_state(state):
				solved_grid = self._state_to_grid(state)
				self.grid = copy.deepcopy(solved_grid)
				if step_callback is not None:
					self._emit_solution_steps(state, parents, step_callback)
				return solved_grid

			if domains is None:
				h_value, domains = self.evaluate_heuristic(state)
				if h_value == float("inf"):
					continue

			target_cell = self._select_unassigned_cell_mrv(state, domains)
			if target_cell is None:
				solved_grid = self._state_to_grid(state)
				self.grid = copy.deepcopy(solved_grid)
				if step_callback is not None:
					self._emit_solution_steps(state, parents, step_callback)
				return solved_grid

			row, col = target_cell
			current_g = self._count_assignments_from_initial(state)

			for value in sorted(domains[target_cell]):
				if not self._is_value_consistent(state, row, col, value):
					continue

				if step_callback is not None and self.emit_search_trace:
					step_callback(row, col, value)

				child_state = self._assign_value(state, row, col, value)
				if child_state in closed:
					if step_callback is not None and self.emit_search_trace:
						step_callback(row, col, 0)
					continue

				child_g = current_g + 1
				previous_best_g = best_g.get(child_state)
				if previous_best_g is not None and child_g <= previous_best_g:
					if step_callback is not None and self.emit_search_trace:
						step_callback(row, col, 0)
					continue

				child_h, child_domains = self.evaluate_heuristic(child_state)
				if child_h == float("inf"):
					if step_callback is not None and self.emit_search_trace:
						step_callback(row, col, 0)
					continue

				best_g[child_state] = child_g
				parents[child_state] = (state, (row, col, value))

				child_f = child_g + child_h
				heapq.heappush(
					pq,
					(child_f, child_h, -child_g, next(serial), child_state, child_domains),
				)

				if step_callback is not None and self.emit_search_trace:
					step_callback(row, col, 0)

		return None

	def evaluate_heuristic(self, state: State) -> Tuple[float, DomainMap]:
		"""Compute h(s) with admissible unassigned-cells heuristic.

		AC-3 mode:
		- Build domains from current partial assignment.
		- Run AC-3 to propagate row/column + inequality constraints.
		- If any domain becomes empty, state is inconsistent and h(s)=inf.
		- Otherwise, h(s) = number of unassigned cells U(s).

		Non-AC-3 mode (fallback):
		- Skip AC-3 and rely on MRV only for variable ordering.
		"""
		domains = self._initialize_domains(state)

		if self.use_ac3:
			if not self._ac3(domains):
				return float("inf"), domains

		if any(len(values) == 0 for values in domains.values()):
			return float("inf"), domains

		return float(self._count_unassigned_cells(state)), domains

	def _initialize_domains(self, state: State) -> DomainMap:
		domains: DomainMap = {}
		for row in range(self.n):
			for col in range(self.n):
				current = state[row][col]
				if current != 0:
					domains[(row, col)] = {current}
					continue

				candidates = {
					value
					for value in range(1, self.n + 1)
					if self._is_value_consistent(state, row, col, value)
				}
				domains[(row, col)] = candidates

		return domains

	def _build_neighbors(self) -> Dict[Cell, Set[Cell]]:
		neighbors: Dict[Cell, Set[Cell]] = {(row, col): set() for row in range(self.n) for col in range(self.n)}

		for row in range(self.n):
			for col_a in range(self.n):
				for col_b in range(self.n):
					if col_a == col_b:
						continue
					neighbors[(row, col_a)].add((row, col_b))

		for col in range(self.n):
			for row_a in range(self.n):
				for row_b in range(self.n):
					if row_a == row_b:
						continue
					neighbors[(row_a, col)].add((row_b, col))

		return neighbors

	def _ac3(self, domains: DomainMap) -> bool:
		queue: Deque[Tuple[Cell, Cell]] = deque(
			(cell_i, cell_j)
			for cell_i in self.cells
			for cell_j in self.neighbors[cell_i]
		)

		while queue:
			cell_i, cell_j = queue.popleft()
			if self._revise(domains, cell_i, cell_j):
				if len(domains[cell_i]) == 0:
					return False

				for cell_k in self.neighbors[cell_i]:
					if cell_k != cell_j:
						queue.append((cell_k, cell_i))

		return True

	def _revise(self, domains: DomainMap, cell_i: Cell, cell_j: Cell) -> bool:
		revised = False
		supported_values: Set[int] = set()

		for value_i in domains[cell_i]:
			if any(
				self._pair_satisfies(cell_i, value_i, cell_j, value_j)
				for value_j in domains[cell_j]
			):
				supported_values.add(value_i)

		if supported_values != domains[cell_i]:
			domains[cell_i] = supported_values
			revised = True

		return revised

	def _pair_satisfies(self, cell_i: Cell, value_i: int, cell_j: Cell, value_j: int) -> bool:
		row_i, col_i = cell_i
		row_j, col_j = cell_j

		# Latin-square constraints: values cannot repeat in the same row/column.
		if row_i == row_j and col_i != col_j and value_i == value_j:
			return False
		if col_i == col_j and row_i != row_j and value_i == value_j:
			return False

		# Horizontal inequality constraints for adjacent cells.
		if row_i == row_j and abs(col_i - col_j) == 1:
			left_col = min(col_i, col_j)
			sign = self.horizontal[row_i][left_col]
			if sign != 0:
				if col_i == left_col:
					left_val, right_val = value_i, value_j
				else:
					left_val, right_val = value_j, value_i

				if sign == 1 and not (left_val < right_val):
					return False
				if sign == -1 and not (left_val > right_val):
					return False

		# Vertical inequality constraints for adjacent cells.
		if col_i == col_j and abs(row_i - row_j) == 1:
			top_row = min(row_i, row_j)
			sign = self.vertical[top_row][col_i]
			if sign != 0:
				if row_i == top_row:
					top_val, bottom_val = value_i, value_j
				else:
					top_val, bottom_val = value_j, value_i

				if sign == 1 and not (top_val < bottom_val):
					return False
				if sign == -1 and not (top_val > bottom_val):
					return False

		return True

	def _select_unassigned_cell_mrv(self, state: State, domains: DomainMap) -> Optional[Cell]:
		unassigned_cells = [
			(row, col)
			for row in range(self.n)
			for col in range(self.n)
			if state[row][col] == 0
		]

		if not unassigned_cells:
			return None

		return min(unassigned_cells, key=lambda cell: (len(domains[cell]), cell[0], cell[1]))

	def _is_initial_state_valid(self, state: State) -> bool:
		for (row, col), clue_value in self.givens.items():
			if state[row][col] != clue_value:
				return False

		for row in range(self.n):
			for col in range(self.n):
				value = state[row][col]
				if value == 0:
					continue

				temp = [list(line) for line in state]
				temp[row][col] = 0
				if not self._is_value_consistent(self._grid_to_state(temp), row, col, value):
					return False

		return True

	def _is_value_consistent(self, state: State, row: int, col: int, value: int) -> bool:
		if not (1 <= value <= self.n):
			return False

		given_value = self.givens.get((row, col))
		if given_value is not None and value != given_value:
			return False

		current = state[row][col]
		if current != 0 and current != value:
			return False

		for c in range(self.n):
			if c != col and state[row][c] == value:
				return False

		for r in range(self.n):
			if r != row and state[r][col] == value:
				return False

		if col < self.n - 1:
			sign = self.horizontal[row][col]
			right = state[row][col + 1]
			if sign != 0 and right != 0:
				if sign == 1 and not (value < right):
					return False
				if sign == -1 and not (value > right):
					return False

		if col > 0:
			sign = self.horizontal[row][col - 1]
			left = state[row][col - 1]
			if sign != 0 and left != 0:
				if sign == 1 and not (left < value):
					return False
				if sign == -1 and not (left > value):
					return False

		if row < self.n - 1:
			sign = self.vertical[row][col]
			bottom = state[row + 1][col]
			if sign != 0 and bottom != 0:
				if sign == 1 and not (value < bottom):
					return False
				if sign == -1 and not (value > bottom):
					return False

		if row > 0:
			sign = self.vertical[row - 1][col]
			top = state[row - 1][col]
			if sign != 0 and top != 0:
				if sign == 1 and not (top < value):
					return False
				if sign == -1 and not (top > value):
					return False

		return True

	def _is_goal_state(self, state: State) -> bool:
		for row in range(self.n):
			for col in range(self.n):
				if state[row][col] == 0:
					return False
		return True

	def _count_unassigned_cells(self, state: State) -> int:
		return sum(1 for row in state for value in row if value == 0)

	def _count_filled_cells(self, state: State) -> int:
		return sum(1 for row in state for value in row if value != 0)

	def _count_assignments_from_initial(self, state: State) -> int:
		return self._count_filled_cells(state) - self.initial_filled_cells

	def _assign_value(self, state: State, row: int, col: int, value: int) -> State:
		grid = [list(line) for line in state]
		grid[row][col] = value
		return self._grid_to_state(grid)

	def _emit_solution_steps(
		self,
		final_state: State,
		parents: Dict[State, Tuple[State, Tuple[int, int, int]]],
		step_callback: StepCallback,
	) -> None:
		moves: List[Tuple[int, int, int]] = []
		state = final_state

		while state in parents:
			parent_state, move = parents[state]
			moves.append(move)
			state = parent_state

		for row, col, value in reversed(moves):
			step_callback(row, col, value)

	@staticmethod
	def _grid_to_state(grid: List[List[int]]) -> State:
		return tuple(tuple(row) for row in grid)

	@staticmethod
	def _state_to_grid(state: State) -> List[List[int]]:
		return [list(row) for row in state]


def solve_with_astar(
	puzzle: PuzzleCase,
	step_callback: Optional[StepCallback] = None,
	use_ac3: bool = True,
) -> Optional[List[List[int]]]:
	"""Functional wrapper to solve a puzzle with A*.

	This helper exists for users who prefer function-style invocation instead of
	instantiating AStarSolver directly.
	"""
	solver = AStarSolver(puzzle, use_ac3=use_ac3)
	return solver.solve(step_callback=step_callback)


