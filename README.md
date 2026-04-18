Cấu trúc project
```bash
Source/ 
├── assets/
├── Inputs/                 # Chứa input-01.txt đến input-10.txt
├── Outputs/                # Chứa kết quả output-01.txt đến output-10.txt
├── src
│    ├── __init__.py
│    ├── gui/                               # lo giao diện
│    ├── domain/                            # Logic game (trước đây là puzzle.py và core/board.py)        
│    │   ├── __init__.py
│    │   └── puzzle.py                      # class Puzzle: is_valid(i, j, val), is_complete(), get_empty_cells(), copy()
│    ├── kb/                                # Xử lý Logic FOL
│    │   ├── __init__.py
│    │   ├── fol_kb.py                      # convert Puzzle → CNF clauses
│    │   └── horn_converter.py              # chuyển đổi kb sang Horn Clause cho BC và FC
│    ├── solvers/                           # Chứa các thuật toán giải đố
│    │   ├── __init__.py
│    │   ├── solver.py                      # Class cha cho mọi thuật toán(đều phải import và implement hàm solve)
│    │   ├── forward.py                     # (Yêu cầu 3) Suy diễn tiến
│    │   ├── backward.py                    # (Yêu cầu 4) Suy diễn lùi
│    │   ├── astar.py                       # (Yêu cầu 5) Thuật toán A*
│    │   ├── brute_force.py                 # (Yêu cầu 6)
│    │   ├── backtrack.py                   # (Yêu cầu 6) Brute-force / Backtracking
│    │   └── utils.py                       # Các hàm hỗ trợ 
│    └── file_io.py                         # đọc xuất file (chỉ đọc chứ k xử lý dữ liệu)
├── main.py                 # File thực thi chính để điều phối
├── README.md               # Hướng dẫn chạy code
└── requirements.txt        # Các thư viện cần thiết
```

---

Mô hình quan hệ:
```bash
domain      ← không phụ thuộc ai
   ↑
   kb       ← phụ thuộc domain
   ↑
solvers     ← phụ thuộc domain + kb
   ↑
main/gui    ← phụ thuộc tất cả
```

---

Workflow:
```bash
Input file
   ↓
io.reader
   ↓
Puzzle (domain)
   ↓
+----------------------+
|      SOLVER          |
|                      |
|  A* / Backtracking   | ← dùng trực tiếp Puzzle
|                      |
|  Forward / Backward  | ← cần KB
|        ↓             |
|     FOLKB            |
+----------------------+
   ↓
Result
   ↓
io.writer / GUI
```
