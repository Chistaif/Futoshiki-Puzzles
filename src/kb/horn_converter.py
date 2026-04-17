"""Chuyển đổi puzzle Futoshiki thành tập Horn clauses dùng cho Backward Chaining và Forward Chaining.

Horn clause có dạng: Head :- Body1, Body2, ...
Tức là: nếu tất cả body đúng thì head đúng.

Các loại atom được dùng:
    ("val",      (i, j, v))   - ô (i,j) mang giá trị v
    ("given",    (i, j, v))   - ô (i,j) được cho sẵn giá trị v (fact)
    ("less_h",   (i, j))      - có dấu < ngang giữa (i,j) và (i,j+1)
    ("greater_h",(i, j))      - có dấu > ngang giữa (i,j) và (i,j+1)
    ("less_v",   (i, j))      - có dấu < dọc giữa (i,j) và (i+1,j)
    ("greater_v",(i, j))      - có dấu > dọc giữa (i,j) và (i+1,j)
    ("less",     (v1, v2))    - v1 < v2 (arithmetic fact)
    ("neq",      (x, y))      - x != y (fact, dùng cho cả index và value)
    ("not_val",  (i, j, v))   - ô (i,j) KHÔNG thể mang giá trị v (negative constraint)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple, Set, Union

from src.domain.puzzle import PuzzleCase

Atom = Tuple  # ví dụ: ("val", (0, 1, 3))
Body = List[Atom]


@dataclass
class HornClause:
    """Một Horn clause gồm head và danh sách body atoms."""
    head: Atom
    body: Body = field(default_factory=list)

    def is_fact(self) -> bool:
        """Fact là clause không có body - luôn đúng."""
        return len(self.body) == 0

    def __repr__(self) -> str:
        if self.is_fact():
            return f"{self.head}."
        body_str = ", ".join(str(b) for b in self.body)
        return f"{self.head} :- {body_str}"


@dataclass
class HornKB:
    """Toàn bộ Horn KB gồm facts và rules.

    Tách biệt facts và rules giúp FC/BC truy cập nhanh hơn
    thay vì phải scan toàn bộ clause list mỗi lần.
    """
    facts: List[Union[HornClause, Atom]] = field(default_factory=list)
    rules: List[HornClause] = field(default_factory=list)

    def all_clauses(self) -> List[Union[HornClause, Atom]]:
        return self.facts + self.rules

    def fact_atoms(self) -> Set[Atom]:
        """Trả về tập các atom đã được chứng minh là đúng (từ facts)."""
        atoms: Set[Atom] = set()
        for fact in self.facts:
            if isinstance(fact, HornClause):
                atoms.add(fact.head)
            else:
                atoms.add(fact)
        return atoms


class HornConverter:
    """Chuyển một PuzzleCase thành HornKB.

    Quá trình:
    1. Build arithmetic facts: less(v1,v2) và neq(x,y)
    2. Build puzzle facts: given, less_h, greater_h, less_v, greater_v
    3. Build rules từ FOL axioms đã được ground xuống domain {0..n-1} x {1..n}

    Lưu ý: A1 (mỗi ô có ít nhất 1 giá trị) là ràng buộc tồn tại/disjunction, không biểu diễn
    trực tiếp được bằng definite Horn. Ràng buộc này thường do chiến lược search/choice xử lý.
    """

    def __init__(self, puzzle: PuzzleCase) -> None:
        self.n = puzzle.n
        self.grid = puzzle.grid
        self.horizontal = puzzle.horizontal
        self.vertical = puzzle.vertical

    # =========================================================================
    # PUBLIC
    # =========================================================================

    def build(self) -> HornKB:
        """Build và trả về toàn bộ Horn KB cho puzzle này."""
        kb = HornKB()
        self._build_arithmetic_facts(kb)
        self._build_puzzle_facts(kb)
        self._build_given_rule(kb)
        self._build_cell_uniqueness_rules(kb)
        self._build_row_uniqueness_rules(kb)
        self._build_col_uniqueness_rules(kb)
        self._build_horizontal_rules(kb)
        self._build_vertical_rules(kb)
        return kb

    # =========================================================================
    # ARITHMETIC FACTS  (background knowledge, không phụ thuộc puzzle cụ thể)
    # =========================================================================

    def _build_arithmetic_facts(self, kb: HornKB) -> None:
        """Tạo các arithmetic facts: less(v1,v2) và neq(x,y).

        Đây là background knowledge - đúng với mọi puzzle kích thước n.
        less(v1,v2) tương đương với v1 < v2 trong toán học.
        neq(x,y)    tương đương với x != y, dùng cho cả chỉ số và giá trị.
        """
        # neq cho chỉ số hàng/cột (0..n-1)
        for x in range(self.n):
            for y in range(self.n):
                if x != y:
                    kb.facts.append(HornClause(head=("neq", (x, y))))

        # less/neq cho giá trị miền (1..n)
        for v1 in range(1, self.n + 1):
            for v2 in range(1, self.n + 1):
                if v1 < v2:
                    # less(v1, v2) - fact vô điều kiện
                    kb.facts.append(HornClause(head=("less", (v1, v2))))
                if v1 != v2:
                    # neq(v1, v2) - fact vô điều kiện
                    kb.facts.append(HornClause(head=("neq", (v1, v2))))

    # =========================================================================
    # PUZZLE FACTS  (phụ thuộc vào input cụ thể)
    # =========================================================================

    def _build_puzzle_facts(self, kb: HornKB) -> None:
        """Tạo facts từ dữ liệu puzzle: ô đã cho, dấu bất đẳng thức."""
        self._build_given_facts(kb)
        self._build_inequality_facts(kb)

    def _build_given_facts(self, kb: HornKB) -> None:
        """Given(i,j,v) - ô được điền sẵn, đây là fact không cần chứng minh."""
        for i in range(self.n):
            for j in range(self.n):
                v = self.grid[i][j]
                if v != 0:
                    kb.facts.append(HornClause(head=("given", (i, j, v))))

    def _build_inequality_facts(self, kb: HornKB) -> None:
        """LessH, GreaterH, LessV, GreaterV - các dấu bất đẳng thức là facts."""
        # Horizontal: horizontal[i][j] là dấu giữa (i,j) và (i,j+1)
        for i in range(self.n):
            for j in range(self.n - 1):
                sign = self.horizontal[i][j]
                if sign == 1:
                    kb.facts.append(HornClause(head=("less_h", (i, j))))
                elif sign == -1:
                    kb.facts.append(HornClause(head=("greater_h", (i, j))))

        # Vertical: vertical[i][j] là dấu giữa (i,j) và (i+1,j)
        for i in range(self.n - 1):
            for j in range(self.n):
                sign = self.vertical[i][j]
                if sign == 1:
                    kb.facts.append(HornClause(head=("less_v", (i, j))))
                elif sign == -1:
                    kb.facts.append(HornClause(head=("greater_v", (i, j))))

    # =========================================================================
    # RULES từ FOL axioms (đã ground xuống domain cụ thể)
    # =========================================================================

    def _build_given_rule(self, kb: HornKB) -> None:
        """A9: Given(i,j,v) -> Val(i,j,v)

        Nếu ô được cho sẵn giá trị v thì Val(i,j,v) đúng.
        Ground rule - mỗi (i,j,v) là một clause riêng.
        """
        for i in range(self.n):
            for j in range(self.n):
                for v in range(1, self.n + 1):
                    kb.rules.append(HornClause(
                        head=("val", (i, j, v)),
                        body=[("given", (i, j, v))],
                    ))

    def _build_cell_uniqueness_rules(self, kb: HornKB) -> None:
        """A2 (Horn hóa): Val(i,j,v1) ∧ neq(v1,v2) -> not_val(i,j,v2).

        Với cùng một ô, nếu đã chọn v1 thì mọi giá trị khác v2 đều bị loại.
        Đây là biểu diễn definite-Horn của ràng buộc "mỗi ô có tối đa 1 giá trị".
        """
        for i in range(self.n):
            for j in range(self.n):
                for v1 in range(1, self.n + 1):
                    for v2 in range(1, self.n + 1):
                        if v1 == v2:
                            continue
                        kb.rules.append(HornClause(
                            head=("not_val", (i, j, v2)),
                            body=[
                                ("val", (i, j, v1)),
                                ("neq", (v1, v2)),
                            ],
                        ))

    def _build_row_uniqueness_rules(self, kb: HornKB) -> None:
        """A3: Val(i,j1,v) ∧ neq(j1,j2) -> not_val(i,j2,v)

        Nếu ô (i,j1) đã mang giá trị v thì không ô nào cùng hàng được mang v.
        Dùng not_val để biểu diễn ràng buộc loại trừ.

        Ground: với mỗi cặp (j1,j2) khác nhau trong cùng hàng i.
        """
        for i in range(self.n):
            for v in range(1, self.n + 1):
                for j1 in range(self.n):
                    for j2 in range(self.n):
                        if j1 == j2:
                            continue
                        # Val(i,j1,v) đúng -> not_val(i,j2,v) đúng
                        kb.rules.append(HornClause(
                            head=("not_val", (i, j2, v)),
                            body=[
                                ("val", (i, j1, v)),
                                ("neq", (j1, j2)),
                            ],
                        ))

    def _build_col_uniqueness_rules(self, kb: HornKB) -> None:
        """A4: Val(i1,j,v) -> not_val(i2,j,v) với i1 != i2.

        Tương tự row uniqueness nhưng theo cột.
        """
        for j in range(self.n):
            for v in range(1, self.n + 1):
                for i1 in range(self.n):
                    for i2 in range(self.n):
                        if i1 == i2:
                            continue
                        kb.rules.append(HornClause(
                            head=("not_val", (i2, j, v)),
                            body=[
                                ("val", (i1, j, v)),
                                ("neq", (i1, i2)),
                            ],
                        ))

    def _build_horizontal_rules(self, kb: HornKB) -> None:
        """A5-A6: Horizontal inequality rules.

        LessH(i,j) ∧ Val(i,j,v1) ∧ NOT less(v1,v2) -> not_val(i,j+1,v2)
        Tức là: nếu có dấu < giữa (i,j) và (i,j+1), và (i,j)=v1,
        thì (i,j+1) không thể là v2 nếu v2 <= v1.

        Tương tự cho GreaterH.

        Lý do dùng not_val thay vì val:
        Horn clause yêu cầu head là atom dương. Ràng buộc inequality
        tự nhiên sinh ra "loại trừ" nên biểu diễn qua not_val hợp lý hơn.
        """
        for i in range(self.n):
            for j in range(self.n - 1):
                sign = self.horizontal[i][j]
                if sign == 0:
                    continue

                for v1 in range(1, self.n + 1):
                    for v2 in range(1, self.n + 1):
                        if sign == 1:
                            # LessH: val(i,j)=v1, cần v1 < v2
                            # Nếu NOT (v1 < v2) thì not_val(i,j+1,v2)
                            if not (v1 < v2):
                                kb.rules.append(HornClause(
                                    head=("not_val", (i, j + 1, v2)),
                                    body=[
                                        ("less_h", (i, j)),
                                        ("val", (i, j, v1)),
                                    ],
                                ))
                            # Ngược lại: val(i,j+1)=v2, cần v1 < v2
                            # Nếu NOT (v1 < v2) thì not_val(i,j,v1)
                            if not (v1 < v2):
                                kb.rules.append(HornClause(
                                    head=("not_val", (i, j, v1)),
                                    body=[
                                        ("less_h", (i, j)),
                                        ("val", (i, j + 1, v2)),
                                    ],
                                ))

                        elif sign == -1:
                            # GreaterH: val(i,j)=v1, cần v1 > v2
                            if not (v1 > v2):
                                kb.rules.append(HornClause(
                                    head=("not_val", (i, j + 1, v2)),
                                    body=[
                                        ("greater_h", (i, j)),
                                        ("val", (i, j, v1)),
                                    ],
                                ))
                            if not (v1 > v2):
                                kb.rules.append(HornClause(
                                    head=("not_val", (i, j, v1)),
                                    body=[
                                        ("greater_h", (i, j)),
                                        ("val", (i, j + 1, v2)),
                                    ],
                                ))

    def _build_vertical_rules(self, kb: HornKB) -> None:
        """A7-A8: Vertical inequality rules.

        Tương tự horizontal nhưng theo chiều dọc giữa (i,j) và (i+1,j).
        """
        for i in range(self.n - 1):
            for j in range(self.n):
                sign = self.vertical[i][j]
                if sign == 0:
                    continue

                for v1 in range(1, self.n + 1):
                    for v2 in range(1, self.n + 1):
                        if sign == 1:
                            # LessV: val(i,j)=v1, cần v1 < v2
                            if not (v1 < v2):
                                kb.rules.append(HornClause(
                                    head=("not_val", (i + 1, j, v2)),
                                    body=[
                                        ("less_v", (i, j)),
                                        ("val", (i, j, v1)),
                                    ],
                                ))
                            if not (v1 < v2):
                                kb.rules.append(HornClause(
                                    head=("not_val", (i, j, v1)),
                                    body=[
                                        ("less_v", (i, j)),
                                        ("val", (i + 1, j, v2)),
                                    ],
                                ))

                        elif sign == -1:
                            # GreaterV: val(i,j)=v1, cần v1 > v2
                            if not (v1 > v2):
                                kb.rules.append(HornClause(
                                    head=("not_val", (i + 1, j, v2)),
                                    body=[
                                        ("greater_v", (i, j)),
                                        ("val", (i, j, v1)),
                                    ],
                                ))
                            if not (v1 > v2):
                                kb.rules.append(HornClause(
                                    head=("not_val", (i, j, v1)),
                                    body=[
                                        ("greater_v", (i, j)),
                                        ("val", (i + 1, j, v2)),
                                    ],
                                ))

