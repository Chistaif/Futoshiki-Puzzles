"""Chuyá»ƒn Ä‘á»•i puzzle Futoshiki thÃ nh táº­p Horn clauses dÃ¹ng cho Backward Chaining vÃ  Forward Chaining.

Horn clause cÃ³ dáº¡ng: Head :- Body1, Body2, ...
Tá»©c lÃ : náº¿u táº¥t cáº£ body Ä‘Ãºng thÃ¬ head Ä‘Ãºng.

CÃ¡c loáº¡i atom Ä‘Æ°á»£c dÃ¹ng:
    ("val",     (i, j, v))   â€” Ã´ (i,j) mang giÃ¡ trá»‹ v
    ("given",   (i, j, v))   â€” Ã´ (i,j) Ä‘Æ°á»£c cho sáºµn giÃ¡ trá»‹ v (fact)
    ("less_h",  (i, j))      â€” cÃ³ dáº¥u < ngang giá»¯a (i,j) vÃ  (i,j+1)
    ("greater_h",(i, j))     â€” cÃ³ dáº¥u > ngang giá»¯a (i,j) vÃ  (i,j+1)
    ("less_v",  (i, j))      â€” cÃ³ dáº¥u < dá»c giá»¯a (i,j) vÃ  (i+1,j)
    ("greater_v",(i, j))     â€” cÃ³ dáº¥u > dá»c giá»¯a (i,j) vÃ  (i+1,j)
    ("less",    (v1, v2))    â€” v1 < v2 (arithmetic fact)
    ("neq",     (x, y))      â€” x â‰  y (fact, dÃ¹ng cho cáº£ index vÃ  value)
    ("not_val", (i, j, v))   â€” Ã´ (i,j) KHÃ”NG thá»ƒ mang giÃ¡ trá»‹ v (negative constraint)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple, Set, Union

from src.domain.puzzle import PuzzleCase

Atom = Tuple  # vÃ­ dá»¥: ("val", (0, 1, 3))
Body = List[Atom]


@dataclass
class HornClause:
    """Má»™t Horn clause gá»“m head vÃ  danh sÃ¡ch body atoms."""
    head: Atom
    body: Body = field(default_factory=list)

    def is_fact(self) -> bool:
        """Fact lÃ  clause khÃ´ng cÃ³ body - luÃ´n Ä‘Ãºng."""
        return len(self.body) == 0

    def __repr__(self) -> str:
        if self.is_fact():
            return f"{self.head}."
        body_str = ", ".join(str(b) for b in self.body)
        return f"{self.head} :- {body_str}"


@dataclass
class HornKB:
    """ToÃ n bá»™ Horn KB gá»“m facts vÃ  rules.

    TÃ¡ch biá»‡t facts vÃ  rules giÃºp FC/BC truy cáº­p nhanh hÆ¡n
    thay vÃ¬ pháº£i scan toÃ n bá»™ clause list má»—i láº§n.
    """
    facts: List[Union[HornClause, Atom]] = field(default_factory=list)
    rules: List[HornClause] = field(default_factory=list)

    def all_clauses(self) -> List[Union[HornClause, Atom]]:
        return self.facts + self.rules

    def fact_atoms(self) -> Set[Atom]:
        """Tráº£ vá» táº­p cÃ¡c atom Ä‘Ã£ Ä‘Æ°á»£c chá»©ng minh lÃ  Ä‘Ãºng (tá»« facts)."""
        atoms: Set[Atom] = set()
        for fact in self.facts:
            if isinstance(fact, HornClause):
                atoms.add(fact.head)
            else:
                atoms.add(fact)
        return atoms


class HornConverter:
    """Chuyá»ƒn má»™t PuzzleCase thÃ nh HornKB.

    QuÃ¡ trÃ¬nh:
    1. Build arithmetic facts: less(v1,v2) vÃ  neq(x,y)
    2. Build puzzle facts: given, less_h, greater_h, less_v, greater_v
    3. Build rules tá»« FOL axioms Ä‘Ã£ Ä‘Æ°á»£c ground xuá»‘ng domain {0..n-1} x {1..n}

    LÆ°u Ã½: A1 (má»—i Ã´ cÃ³ Ã­t nháº¥t 1 giÃ¡ trá»‹) lÃ  rÃ ng buá»™c tá»“n táº¡i/disjunction, khÃ´ng biá»ƒu diá»…n
    trá»±c tiáº¿p Ä‘Æ°á»£c báº±ng definite Horn. RÃ ng buá»™c nÃ y thÆ°á»ng do chiáº¿n lÆ°á»£c search/choice xá»­ lÃ½.
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
        """Build vÃ  tráº£ vá» toÃ n bá»™ Horn KB cho puzzle nÃ y."""
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
    # ARITHMETIC FACTS  (background knowledge, khÃ´ng phá»¥ thuá»™c puzzle cá»¥ thá»ƒ)
    # =========================================================================

    def _build_arithmetic_facts(self, kb: HornKB) -> None:
        """Táº¡o cÃ¡c arithmetic facts: less(v1,v2) vÃ  neq(x,y).

        ÄÃ¢y lÃ  background knowledge â€” Ä‘Ãºng vá»›i má»i puzzle kÃ­ch thÆ°á»›c n.
        less(v1,v2) tÆ°Æ¡ng Ä‘Æ°Æ¡ng vá»›i v1 < v2 trong toÃ¡n há»c.
        neq(x,y)    tÆ°Æ¡ng Ä‘Æ°Æ¡ng vá»›i x â‰  y, dÃ¹ng cho cáº£ chá»‰ sá»‘ vÃ  giÃ¡ trá»‹.
        """
        # neq cho chá»‰ sá»‘ hÃ ng/cá»™t (0..n-1)
        for x in range(self.n):
            for y in range(self.n):
                if x != y:
                    kb.facts.append(HornClause(head=("neq", (x, y))))

        # less/neq cho giÃ¡ trá»‹ miá»n (1..n)
        for v1 in range(1, self.n + 1):
            for v2 in range(1, self.n + 1):
                if v1 < v2:
                    # less(v1, v2) â€” fact vÃ´ Ä‘iá»u kiá»‡n
                    kb.facts.append(HornClause(head=("less", (v1, v2))))
                if v1 != v2:
                    # neq(v1, v2) â€” fact vÃ´ Ä‘iá»u kiá»‡n
                    kb.facts.append(HornClause(head=("neq", (v1, v2))))

    # =========================================================================
    # PUZZLE FACTS  (phá»¥ thuá»™c vÃ o input cá»¥ thá»ƒ)
    # =========================================================================

    def _build_puzzle_facts(self, kb: HornKB) -> None:
        """Táº¡o facts tá»« dá»¯ liá»‡u puzzle: Ã´ Ä‘Ã£ cho, dáº¥u báº¥t Ä‘áº³ng thá»©c."""
        self._build_given_facts(kb)
        self._build_inequality_facts(kb)

    def _build_given_facts(self, kb: HornKB) -> None:
        """Given(i,j,v) â€” Ã´ Ä‘Æ°á»£c Ä‘iá»n sáºµn, Ä‘Ã¢y lÃ  fact khÃ´ng cáº§n chá»©ng minh."""
        for i in range(self.n):
            for j in range(self.n):
                v = self.grid[i][j]
                if v != 0:
                    kb.facts.append(HornClause(head=("given", (i, j, v))))

    def _build_inequality_facts(self, kb: HornKB) -> None:
        """LessH, GreaterH, LessV, GreaterV â€” cÃ¡c dáº¥u báº¥t Ä‘áº³ng thá»©c lÃ  facts."""
        # Horizontal: horizontal[i][j] lÃ  dáº¥u giá»¯a (i,j) vÃ  (i,j+1)
        for i in range(self.n):
            for j in range(self.n - 1):
                sign = self.horizontal[i][j]
                if sign == 1:
                    kb.facts.append(HornClause(head=("less_h", (i, j))))
                elif sign == -1:
                    kb.facts.append(HornClause(head=("greater_h", (i, j))))

        # Vertical: vertical[i][j] lÃ  dáº¥u giá»¯a (i,j) vÃ  (i+1,j)
        for i in range(self.n - 1):
            for j in range(self.n):
                sign = self.vertical[i][j]
                if sign == 1:
                    kb.facts.append(HornClause(head=("less_v", (i, j))))
                elif sign == -1:
                    kb.facts.append(HornClause(head=("greater_v", (i, j))))

    # =========================================================================
    # RULES tá»« FOL axioms (Ä‘Ã£ ground xuá»‘ng domain cá»¥ thá»ƒ)
    # =========================================================================

    def _build_given_rule(self, kb: HornKB) -> None:
        """A9: Given(i,j,v) â†’ Val(i,j,v)

        Náº¿u Ã´ Ä‘Æ°á»£c cho sáºµn giÃ¡ trá»‹ v thÃ¬ Val(i,j,v) Ä‘Ãºng.
        Ground rule â€” má»—i (i,j,v) lÃ  má»™t clause riÃªng.
        """
        for i in range(self.n):
            for j in range(self.n):
                for v in range(1, self.n + 1):
                    kb.rules.append(HornClause(
                        head=("val", (i, j, v)),
                        body=[("given", (i, j, v))],
                    ))

    def _build_cell_uniqueness_rules(self, kb: HornKB) -> None:
        """A2 (Horn hÃ³a): Val(i,j,v1) âˆ§ neq(v1,v2) â†’ not_val(i,j,v2).

        Vá»›i cÃ¹ng má»™t Ã´, náº¿u Ä‘Ã£ chá»n v1 thÃ¬ má»i giÃ¡ trá»‹ khÃ¡c v2 Ä‘á»u bá»‹ loáº¡i.
        ÄÃ¢y lÃ  biá»ƒu diá»…n definite-Horn cá»§a rÃ ng buá»™c "má»—i Ã´ cÃ³ tá»‘i Ä‘a 1 giÃ¡ trá»‹".
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
        """A3: Val(i,j1,v) âˆ§ neq(j1,j2) â†’ not_val(i,j2,v)

        Náº¿u Ã´ (i,j1) Ä‘Ã£ mang giÃ¡ trá»‹ v thÃ¬ khÃ´ng Ã´ nÃ o cÃ¹ng hÃ ng Ä‘Æ°á»£c mang v.
        DÃ¹ng not_val Ä‘á»ƒ biá»ƒu diá»…n rÃ ng buá»™c loáº¡i trá»«.

        Ground: vá»›i má»—i cáº·p (j1,j2) khÃ¡c nhau trong cÃ¹ng hÃ ng i.
        """
        for i in range(self.n):
            for v in range(1, self.n + 1):
                for j1 in range(self.n):
                    for j2 in range(self.n):
                        if j1 == j2:
                            continue
                        # Val(i,j1,v) Ä‘Ãºng â†’ not_val(i,j2,v) Ä‘Ãºng
                        kb.rules.append(HornClause(
                            head=("not_val", (i, j2, v)),
                            body=[
                                ("val", (i, j1, v)),
                                ("neq", (j1, j2)),
                            ],
                        ))

    def _build_col_uniqueness_rules(self, kb: HornKB) -> None:
        """A4: Val(i1,j,v) â†’ not_val(i2,j,v) vá»›i i1 â‰  i2

        TÆ°Æ¡ng tá»± row uniqueness nhÆ°ng theo cá»™t.
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

        LessH(i,j) âˆ§ Val(i,j,v1) âˆ§ NOT less(v1,v2) â†’ not_val(i,j+1,v2)
        Tá»©c lÃ : náº¿u cÃ³ dáº¥u < giá»¯a (i,j) vÃ  (i,j+1), vÃ  (i,j)=v1,
        thÃ¬ (i,j+1) khÃ´ng thá»ƒ lÃ  v2 náº¿u v2 â‰¤ v1.

        TÆ°Æ¡ng tá»± cho GreaterH.

        LÃ½ do dÃ¹ng not_val thay vÃ¬ val:
        Horn clause yÃªu cáº§u head lÃ  atom dÆ°Æ¡ng. RÃ ng buá»™c inequality
        tá»± nhiÃªn sinh ra "loáº¡i trá»«" nÃªn biá»ƒu diá»…n qua not_val há»£p lÃ½ hÆ¡n.
        """
        for i in range(self.n):
            for j in range(self.n - 1):
                sign = self.horizontal[i][j]
                if sign == 0:
                    continue

                for v1 in range(1, self.n + 1):
                    for v2 in range(1, self.n + 1):
                        if sign == 1:
                            # LessH: val(i,j)=v1, cáº§n v1 < v2
                            # Náº¿u NOT (v1 < v2) thÃ¬ not_val(i,j+1,v2)
                            if not (v1 < v2):
                                kb.rules.append(HornClause(
                                    head=("not_val", (i, j + 1, v2)),
                                    body=[
                                        ("less_h", (i, j)),
                                        ("val", (i, j, v1)),
                                    ],
                                ))
                            # NgÆ°á»£c láº¡i: val(i,j+1)=v2, cáº§n v1 < v2
                            # Náº¿u NOT (v1 < v2) thÃ¬ not_val(i,j,v1)
                            if not (v1 < v2):
                                kb.rules.append(HornClause(
                                    head=("not_val", (i, j, v1)),
                                    body=[
                                        ("less_h", (i, j)),
                                        ("val", (i, j + 1, v2)),
                                    ],
                                ))

                        elif sign == -1:
                            # GreaterH: val(i,j)=v1, cáº§n v1 > v2
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

        TÆ°Æ¡ng tá»± horizontal nhÆ°ng theo chiá»u dá»c giá»¯a (i,j) vÃ  (i+1,j).
        """
        for i in range(self.n - 1):
            for j in range(self.n):
                sign = self.vertical[i][j]
                if sign == 0:
                    continue

                for v1 in range(1, self.n + 1):
                    for v2 in range(1, self.n + 1):
                        if sign == 1:
                            # LessV: val(i,j)=v1, cáº§n v1 < v2
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
                            # GreaterV: val(i,j)=v1, cáº§n v1 > v2
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

