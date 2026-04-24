<div align="center">

# ♠️ **FUTOSHIKI PUZZLES SOLVER**
### *AI-Powered Futoshiki Puzzle Solver - Giải Futoshiki Bằng Trí Tuệ Nhân Tạo*

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Pygame](https://img.shields.io/badge/Pygame-GUI-00B140?logo=pygame&logoColor=white)](https://pygame.org)
[![PySAT](https://img.shields.io/badge/PySAT-Logic%20Solving-FF6B35?logo=python&logoColor=white)](https://pysathq.github.io/)
[![AI](https://img.shields.io/badge/AI-Search%20Algorithms-FF6B35?logo=artificial-intelligence)](https://en.wikipedia.org/wiki/Search_algorithm)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/Status-Completed-success)](https://github.com)

---

### **ĐẠI HỌC QUỐC GIA TP.HCM**
### **TRƯỜNG ĐẠI HỌC KHOA HỌC TỰ NHIÊN**
### **KHOA CÔNG NGHỆ THÔNG TIN**

**Môn học:** CSC14003 - Cơ Sở Trí Tuệ Nhân Tạo  
**Đồ án:** Project 2 - Futoshiki Puzzles Solver  
**Năm học:** 2025 - 2026

---

### **NHÓM SINH VIÊN THỰC HIỆN**

| MSSV | Họ và Tên | Vai Trò |
|------|-----------|---------|
| 24127252 | Nguyễn Khánh Toàn | Thành viên |
| 24127529 | Nguyễn Chí Tài | Nhóm Trưởng |
| 24127545 | Nguyễn Ngọc Thiên | Thành viên |
| 24127250 | Phan Quang Tiến | Thành viên |

</div>

---

## 📖 **Giới Thiệu**

**Futoshiki Puzzles Solver** là ứng dụng giải đố **Futoshiki** tự động bằng trí tuệ nhân tạo. Dự án hỗ trợ nhiều hướng tiếp cận khác nhau, từ suy diễn logic đến tìm kiếm trạng thái, đồng thời cung cấp giao diện đồ họa để người dùng chơi thủ công hoặc quan sát quá trình solver chạy.

### 🎯 **Mục tiêu dự án**

- Mô hình hóa đúng luật chơi Futoshiki trên nhiều kích thước bảng.
- Xây dựng các solver AI có cấu trúc rõ ràng và dễ mở rộng.
- So sánh hiệu năng giữa các phương pháp giải khác nhau.
- Cung cấp GUI trực quan cho thao tác thủ công và chạy AI.

---

## ✨ **Tính Năng Chính**

### **Giao Diện Đồ Họa (GUI)**
- Giao diện xem bảng puzzle, nhập lựa chọn và theo dõi trạng thái bài toán.
- Hỗ trợ chơi thủ công và xem solver tự động chạy.
- Hiển thị các ràng buộc bất đẳng thức giữa các ô.

### **Các Bộ Giải Đa Phương Pháp**
- **Forward Chaining** - suy diễn tiến trên Horn clauses.
- **Backward Chaining** - suy diễn lùi dựa trên KB logic.
- **A\* Search** - tìm kiếm có heuristic.
- **Brute-force / Backtracking** - duyệt lời giải theo ràng buộc.
- **SAT Solver** - chuyển bài toán sang CNF và giải bằng PySAT.

### **I/O và Kiểm Thử**
- Đọc dữ liệu từ thư mục `Inputs/` và ghi kết quả ra `Outputs/`.
- Có bộ test cho các solver trong `src/tests/`.
- Hỗ trợ chạy hàng loạt để so sánh kết quả giữa các input.

---

## 📊 **Workflow**

```bash
Input file
   ↓
file_io.reader
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
|       FOLKB          |
+----------------------+
   ↓
Result
   ↓
file_io.writer / GUI
```

---

## 🛠️ **Công Nghệ Sử Dụng**

| Thư Viện | Mục Đích |
|----------|----------|
| **Python** | Ngôn ngữ lập trình chính |
| **Pygame** | Xây dựng giao diện đồ họa |
| **python-sat** | Giải bài toán logic dưới dạng SAT |
| **pytest** | Kiểm thử tự động |

---

## 📦 **Cài Đặt**

### **Yêu cầu hệ thống**

- Python 3.10 trở lên
- `pip`
- Windows / macOS / Linux

### **Các bước cài đặt**

**Bước 1: Clone repository**

```bash
git clone <repository-url>
cd Futoshiki-Puzzles
```

**Bước 2: Cài dependencies**

```bash
pip install -r requirements.txt
```

**Bước 3: Chạy chương trình**

```bash
python main.py
```

---

## 🎮 **Hướng Dẫn Sử Dụng**

### **1. Chế độ GUI**

Chạy ứng dụng bằng:

```bash
python main.py
```

Trong giao diện chính, bạn có thể:

- Chọn một bộ puzzle từ menu.
- Vào chế độ chơi thủ công để nhập giá trị vào các ô trống.
- Chạy AI Solver để quan sát quá trình giải tự động.

### **2. Chế độ giải tự động**

Bạn có thể chọn từng solver theo nhu cầu:

- Forward Chaining
- Backward Chaining
- A* Search
- Brute-force / Backtracking
- SAT Solver

Kết quả được hiển thị trực tiếp trên bảng và có thể lưu ra file đầu ra tương ứng.

---

## 🏗️ **Cấu Trúc Dự Án**

```bash
Futoshiki-Puzzles/
├── Inputs/                   # Chứa input-01.txt đến input-10.txt
├── Outputs/                  # Chứa output-01.txt đến output-10.txt
├── src/
│   ├── gui/                  # Giao diện người dùng
│   ├── domain/               # Logic game và mô hình Puzzle
│   ├── kb/                   # Xử lý logic FOL / Horn clauses
│   └── solvers/              # Các thuật toán giải đố
├── main.py                   # File thực thi chính
├── README.md                 # Hướng dẫn chạy và mô tả dự án
└── requirements.txt          # Các thư viện cần thiết
```

### **Mô hình quan hệ**

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

## 🧪 **Chạy Tests**

Chạy toàn bộ test suite:

```bash
pytest
```

Chạy riêng bộ test solver:

```bash
pytest src/tests/test_solvers.py
```

---

## 📚 **Tham Khảo**

- [Futoshiki.com](https://www.futoshiki.com/) - Nguồn tham khảo để lấy input cho đồ án.
- [Futoshiki.uk](https://futoshiki.uk/index.html) - Nguồn tham khảo để đối chiếu output cho đồ án.
- [Video demo YouTube](https://www.youtube.com/watch?v=25V7OLtf4e8)

---

## **Ghi chú**

Dự án được phát triển phục vụ mục đích học tập trong môn CSC14003 - Cơ Sở Trí Tuệ Nhân Tạo.

---

## 🎬 **Demo Gallery**

**1. Menu chính**

<div align="center">
<img width="700px" src="https://github.com/user-attachments/assets/d020ee26-9f41-4253-9132-64494107884b" alt="Menu Demo GIF">
</div>

**2. Chơi thủ công**

<div align="center">
<img width="700px" src="https://github.com/user-attachments/assets/4d8895df-2587-4aa8-b6e8-3c8a1476ab0d" alt="Manual Demo GIF">
</div>

**3. Chế độ AI Solver**

<div align="center">
<img width="700px" src="https://github.com/user-attachments/assets/b1a23e32-f38f-4f4d-8444-41f03c1543d6" alt="AI Solver Demo GIF">
</div>

## 🎥 **Video Demo**

- [Xem demo trên YouTube](https://www.youtube.com/watch?v=25V7OLtf4e8)

---

<div align="center">

## ⭐ **Nếu dự án hữu ích, hãy cho chúng tôi một ngôi sao!**

---

![Footer](https://readme-typing-svg.demolab.com?font=Fira+Code&weight=500&duration=4000&pause=1000&color=F7A800&center=true&vCenter=true&width=700&lines=Thank+you+for+visiting+our+Futoshiki+project!+♠️;Let's+solve+Futoshiki+with+AI+together.;Forward+Chaining+%7C+Backward+Chaining+%7C+A*+%7C+SAT+%7C+Backtracking)

</div>
