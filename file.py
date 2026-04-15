"""Tiện ích đọc và kiểm tra dữ liệu puzzle từ file text.

File này giữ vai trò trung tâm cho việc nạp dữ liệu đầu vào của game:
- đọc từng file puzzle trong thư mục Inputs
- kiểm tra định dạng dữ liệu
- chuẩn hóa dữ liệu thành cấu trúc dễ dùng cho màn game

Mục tiêu của phần này là làm cho luồng nạp puzzle rõ ràng, an toàn và dễ bảo trì.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple


@dataclass(frozen=True)
class PuzzleCase:
    """Một puzzle được nạp từ file input.

    class này gom toàn bộ dữ liệu cần thiết để màn chơi có thể render và xử lý:
    - tên file để hiển thị cho người dùng
    - đường dẫn gốc để truy vết file
    - kích thước bàn cờ
    - grid chứa các số đã cho sẵn
    - horizontal / vertical chứa các ràng buộc lớn hơn / nhỏ hơn
    """

    name: str
    path: Path
    n: int
    grid: List[List[int]]
    horizontal: List[List[int]]
    vertical: List[List[int]]


def _parse_csv_ints(raw_line: str) -> List[int]:
    """Tách một dòng CSV thành danh sách số nguyên.

    Hàm này cố tình kiểm tra chặt để tránh dữ liệu lỗi kiểu:
    - có dấu phẩy thừa
    - có phần tử rỗng
    - có định dạng không đúng với file puzzle
    """
    parts = [part.strip() for part in raw_line.split(",")]
    if any(part == "" for part in parts):
        raise ValueError(f"Invalid CSV line: {raw_line}")
    return [int(part) for part in parts]


def _read_clean_lines(path: Path) -> List[str]:
    """Đọc file và loại bỏ dòng trống hoặc dòng comment.

    Việc làm sạch dữ liệu ngay từ đầu giúp phần parse phía sau đơn giản hơn,
    vì các bước tiếp theo chỉ cần xử lý đúng những dòng thực sự mang dữ liệu.
    """
    raw_lines = path.read_text(encoding="utf-8").splitlines()
    cleaned: List[str] = []
    for line in raw_lines:
        content = line.strip()
        if not content:
            continue
        if content.startswith("#"):
            continue
        cleaned.append(content)
    return cleaned


def _parse_input_file(path: Path) -> PuzzleCase:
    """Parse một file puzzle cụ thể và chuyển thành PuzzleCase.

    Trình tự parse được giữ cố định:
    1. đọc toàn bộ dòng có ý nghĩa
    2. lấy kích thước n
    3. đọc grid
    4. đọc ràng buộc ngang
    5. đọc ràng buộc dọc

    Cách làm này giúp phát hiện lỗi sớm và báo đúng vị trí dữ liệu sai.
    """
    lines = _read_clean_lines(path)
    if not lines:
        raise ValueError(f"Empty puzzle file: {path}")

    # Dòng đầu tiên luôn là kích thước bàn cờ n.
    n = int(lines[0])
    # Số dòng tối thiểu cần có: 1 dòng n, n dòng grid, n dòng horizontal, n-1 dòng vertical.
    expected_lines = 1 + n + n + (n - 1)
    if len(lines) < expected_lines:
        raise ValueError(
            f"Puzzle file {path.name} is incomplete: expected at least {expected_lines} non-empty lines"
        )

    # Cursor dùng để đọc tuần tự từng khối dữ liệu.
    cursor = 1

    # Grid là phần chứa các giá trị cố định ban đầu của puzzle.
    grid: List[List[int]] = []
    for _ in range(n):
        row = _parse_csv_ints(lines[cursor])
        cursor += 1
        if len(row) != n:
            raise ValueError(f"Grid row width mismatch in {path.name}")
        if any(value < 0 or value > n for value in row):
            raise ValueError(f"Grid value out of range [0, {n}] in {path.name}")
        grid.append(row)

    # Horizontal là các ràng buộc giữa ô bên trái và ô bên phải.
    # Giá trị hợp lệ chỉ có:
    # - 1  : ô trái < ô phải
    # - -1 : ô trái > ô phải
    # - 0  : không có ràng buộc
    horizontal: List[List[int]] = []
    for _ in range(n):
        row = _parse_csv_ints(lines[cursor])
        cursor += 1
        if len(row) != n - 1:
            raise ValueError(f"Horizontal row width mismatch in {path.name}")
        if any(value not in (-1, 0, 1) for value in row):
            raise ValueError(f"Horizontal constraint must be -1, 0 or 1 in {path.name}")
        horizontal.append(row)

    # Vertical là các ràng buộc giữa ô phía trên và ô phía dưới.
    vertical: List[List[int]] = []
    for _ in range(n - 1):
        row = _parse_csv_ints(lines[cursor])
        cursor += 1
        if len(row) != n:
            raise ValueError(f"Vertical row width mismatch in {path.name}")
        if any(value not in (-1, 0, 1) for value in row):
            raise ValueError(f"Vertical constraint must be -1, 0 or 1 in {path.name}")
        vertical.append(row)

    # Đóng gói toàn bộ dữ liệu đã parse thành một object duy nhất.
    return PuzzleCase(
        name=path.name,
        path=path,
        n=n,
        grid=grid,
        horizontal=horizontal,
        vertical=vertical,
    )


def load_all_input_puzzles() -> List[PuzzleCase]:
    """Đọc toàn bộ file puzzle hợp lệ trong thư mục Inputs.

    Hàm này chủ động bỏ qua file lỗi thay vì làm dừng cả ứng dụng,
    vì mục tiêu là để UI vẫn chạy được nếu trong Inputs có file hỏng.
    """
    root_path = Path(__file__).resolve().parent
    input_dir = root_path / "Inputs"

    if not input_dir.exists():
        # Không có thư mục Inputs thì trả về danh sách rỗng để UI tự xử lý.
        return []

    puzzle_cases: List[PuzzleCase] = []
    for file_path in sorted(input_dir.glob("*.txt")):
        try:
            puzzle_cases.append(_parse_input_file(file_path))
        except ValueError:
            # Bỏ qua file lỗi để không ảnh hưởng các puzzle hợp lệ khác.
            continue

    return puzzle_cases


def readFile(fileName: str) -> Optional[Tuple[int, List[List[int]], List[List[int]], List[List[int]]]]:
    """Hàm tương thích cho code cũ.

    Một số phần khác của project có thể vẫn gọi readFile() theo kiểu cũ,
    nên mình giữ lại hàm này để tránh phải sửa lan sang nhiều nơi.
    Về bản chất, nó chỉ parse file rồi trả về tuple truyền thống:
    (n, grid, horizontal, vertical)
    """
    case = _parse_input_file(Path(fileName))
    if case.n <= 0:
        return None
    return case.n, case.grid, case.horizontal, case.vertical
