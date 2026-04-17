from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

from src.domain.puzzle import PuzzleCase


def _parse_csv_ints(raw_line: str) -> List[int]:
    parts = [part.strip() for part in raw_line.split(",")]
    if any(part == "" for part in parts):
        raise ValueError(f"Invalid CSV line: {raw_line}")
    return [int(part) for part in parts]


def _read_clean_lines(path: Path) -> List[str]:
    raw_lines = path.read_text(encoding="utf-8").splitlines()
    cleaned: List[str] = []
    for line in raw_lines:
        content = line.strip()
        if not content or content.startswith("#"):
            continue
        cleaned.append(content)
    return cleaned


def _parse_input_file(path: Path) -> PuzzleCase:
    lines = _read_clean_lines(path)
    if not lines:
        raise ValueError(f"Empty puzzle file: {path}")

    n = int(lines[0])
    expected_lines = 1 + n + n + (n - 1)
    if len(lines) < expected_lines:
        raise ValueError(
            f"Puzzle file {path.name} is incomplete: expected at least {expected_lines} non-empty lines"
        )

    cursor = 1
    grid: List[List[int]] = []
    for _ in range(n):
        row = _parse_csv_ints(lines[cursor])
        cursor += 1
        if len(row) != n:
            raise ValueError(f"Grid row width mismatch in {path.name}")
        grid.append(row)

    horizontal: List[List[int]] = []
    for _ in range(n):
        row = _parse_csv_ints(lines[cursor])
        cursor += 1
        if len(row) != n - 1:
            raise ValueError(f"Horizontal row width mismatch in {path.name}")
        horizontal.append(row)

    vertical: List[List[int]] = []
    for _ in range(n - 1):
        row = _parse_csv_ints(lines[cursor])
        cursor += 1
        if len(row) != n:
            raise ValueError(f"Vertical row width mismatch in {path.name}")
        vertical.append(row)

    return PuzzleCase(
        name=path.name,
        path=path,
        n=n,
        grid=grid,
        horizontal=horizontal,
        vertical=vertical,
    )


def load_all_input_puzzles() -> List[PuzzleCase]:
    root_path = Path(__file__).resolve().parents[1]
    input_dir = root_path / "Inputs"
    if not input_dir.exists():
        return []

    puzzle_cases: List[PuzzleCase] = []
    for file_path in sorted(input_dir.glob("*.txt")):
        try:
            puzzle_cases.append(_parse_input_file(file_path))
        except ValueError:
            continue
    return puzzle_cases


def readFile(file_name: str) -> Optional[Tuple[int, List[List[int]], List[List[int]], List[List[int]]]]:
    case = _parse_input_file(Path(file_name))
    if case.n <= 0:
        return None
    return case.n, case.grid, case.horizontal, case.vertical


def write_output(file_name: str, grid: List[List[int]]) -> Path:
    """Write solved grid to Source/Outputs/<file_name>."""
    root_path = Path(__file__).resolve().parents[1]
    output_dir = root_path / "Outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / file_name
    lines = [",".join(str(value) for value in row) for row in grid]
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path

