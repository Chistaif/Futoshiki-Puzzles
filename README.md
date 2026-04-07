# Futoshiki-Puzzles
```
Student_ID1_StudentID2/
├── Inputs/                 # Chứa input-01.txt đến input-10.txt
├── Outputs/                # Chứa kết quả output-01.txt đến output-10.txt
├── Source/                 # Nơi chứa toàn bộ mã nguồn
│   ├── solvers/            # Chứa các thuật toán giải đố
│   │   ├── __init__.py
│   │   ├── base.py         # Class cha cho mọi thuật toán
│   │   ├── fol_kb.py       # (Yêu cầu 2) Tạo Ground KB & CNF
│   │   ├── forward.py      # (Yêu cầu 3) Suy diễn tiến
│   │   ├── backward.py     # (Yêu cầu 4) Suy diễn lùi
│   │   ├── astar.py        # (Yêu cầu 5) Thuật toán A*
│   │   └── backtrack.py    # (Yêu cầu 6) Brute-force / Backtracking
│   ├── puzzle.py           # Class quản lý trạng thái bảng Futoshiki (đọc/ghi file)
│   ├── gui.py              # Class giao diện Tkinter (đã phác thảo ở trên)
│   ├── utils.py            # Hàm hỗ trợ (đo thời gian chạy, bộ nhớ)
│   └── main.py             # File thực thi chính để điều phối
├── README.md               # Hướng dẫn chạy code
└── requirements.txt        # Các thư viện cần thiết (nếu có)
```
