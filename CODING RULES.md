# 🧠 Coding Rules for AI Agent (Python)

## 🎯 Mục tiêu
Tạo code:
- Dễ đọc
- Dễ maintain
- Dễ mở rộng
- Ít bug
- Có structure rõ ràng
- Comment chi tiết trong từng file code

---

## 1. 🧱 Nguyên tắc chung

- Luôn ưu tiên **readability hơn cleverness**
- Code phải **self-explanatory**, comment chi tiết
- Tránh viết code "hack", "tạm bợ"
- Mỗi file / function chỉ nên có **1 trách nhiệm chính (Single Responsibility)**

---

## 2. 🏷️ Naming Convention (PEP 8)

### Biến / Hàm / Thuộc tính
- Dùng **snake_case**
- Tên phải có nghĩa rõ ràng

```python
# ❌ Bad
x = get_data()
userList = fetch_users()
def GetUser(): pass

# ✅ Good
user_list = fetch_users()
def get_user(): pass
```

### Class / Exception
- Dùng **PascalCase**

```python
class UserService:
    pass

class ValidationError(Exception):
    pass
```

### Hằng số (Constants)
- Dùng **UPPER_SNAKE_CASE**

```python
MAX_RETRY = 3
DEFAULT_TIMEOUT = 30
FILE_PATH = "data/input.txt"
```

### Private method / attribute
- Dùng **dấu gạch dưới đầu** `_`

```python
def _internal_helper(self):
    pass

self._cache = {}
```

---

## 3. 📦 Structure & Organization

Tách file theo feature / module, không để file quá 300-500 dòng, mỗi folder có trách nhiệm rõ ràng

```
src/
  ├── solvers/
  │   ├── forward_chaining.py
  │   ├── backward_chaining.py
  │   └── a_star.py
  ├── knowledge_base/
  │   ├── kb_generator.py
  │   └── cnf_converter.py
  ├── models/
  │   └── futoshiki.py
  ├── utils/
  │   ├── file_io.py
  │   └── helpers.py
  └── gui/
      └── menu_screen.py
```

---

## 4. 🔧 Function Design

Hàm nên: ngắn (≤ 30 dòng), làm 1 việc duy nhất, tránh nested quá sâu (max 2-3 levels)

```python
# ❌ Bad
def process():
    if a:
        if b:
            if c:
                do_something()

# ✅ Good
def process():
    if not is_valid():
        return
    handle_logic()
```

---

## 5. 🧼 Clean Code Rules

- Không duplicate code → dùng function / abstraction
- Không hardcode → dùng config / constant
- Tránh magic numbers

```python
# ❌ Bad
if user.age > 18:

# ✅ Good
LEGAL_AGE = 18
if user.age > LEGAL_AGE:
```

---

## 6. ⚠️ Error Handling

Không bỏ qua lỗi, luôn handle rõ ràng

```python
# ❌ Bad
try:
    fetch_data()
except:
    pass

# ✅ Good
try:
    fetch_data()
except FileNotFoundError as e:
    logger.error(f"File not found: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise RuntimeError("Failed to fetch data")
```

---

## 7. 🧪 Testing Mindset

Code phải dễ test, tránh phụ thuộc trực tiếp vào API/Database, dùng dependency injection nếu có thể

```python
# ❌ Bad - khó test
def solve():
    data = read_file("input.txt")  # hardcoded path

# ✅ Good - dễ test
def solve(file_path: str):
    data = read_file(file_path)
```

---

## 8. 🔄 Reusability

Viết function/component có thể tái sử dụng, tránh coupling chặt giữa các module

```python
def is_valid_value(grid: List[List[int]], row: int, col: int, value: int) -> bool:
    """Kiểm tra value có hợp lệ tại ô (row, col) không."""
    pass
```

---

## 9. 🧾 Comment Rules

Comment chi tiết cho file, class, function quan trọng, giải thích "WHY" không phải "WHAT"

```python
# ❌ Bad
i += 1  # tăng i lên 1

# ✅ Good
# Retry mechanism to handle flaky API - tăng số lần thử lại
retry_count += 1

# ✅ Good - Docstring cho function
def check_row_constraint(grid: List[List[int]], row: int) -> bool:
    """
    Kiểm tra hàng có hợp lệ không (mỗi số 1..N xuất hiện đúng 1 lần)
    
    Args:
        grid: Ma trận N x N
        row: Chỉ số hàng cần kiểm tra (0-based)
    
    Returns:
        True nếu hàng hợp lệ, False nếu có số trùng
    """
    pass
```

---

## 10. 🚀 Performance

Không optimize sớm, chỉ tối ưu khi có bottleneck rõ ràng, tránh loop lồng nhau nếu không cần thiết

```python
# ❌ Bad - O(n^3) không cần thiết
for i in range(N):
    for j in range(N):
        for k in range(N):
            do_something()

# ✅ Good
for i in range(N):
    do_something_once(i)
```

---

## 11. 🔒 Security

Không hardcode API keys, Password, Token. Validate input từ user

```python
# ❌ Bad
API_KEY = "abc123xyz"

# ✅ Good
import os
API_KEY = os.environ.get("API_KEY", "")

# Validate input
def read_grid(file_path: str) -> List[List[int]]:
    if not file_path.endswith(".txt"):
        raise ValueError("Chỉ chấp nhận file .txt")
```

---

## 12. 🧩 Extensibility

Code phải dễ mở rộng: không sửa code cũ nhiều khi thêm feature mới, dùng interface/abstraction

```python
from abc import ABC, abstractmethod

class Solver(ABC):
    @abstractmethod
    def solve(self, puzzle) -> Optional[Grid]:
        pass

class ForwardChainingSolver(Solver):
    def solve(self, puzzle):
        # Implementation
        pass
```

---

## 13. 🤖 AI Agent Rules (Quan trọng)

Agent phải:
1. Không generate code dài nếu chưa cần
2. Luôn chia nhỏ problem
3. Luôn: Hiểu requirement → Thiết kế structure → Viết code
4. Nếu không chắc: hỏi lại thay vì đoán

---

## 14. ✅ Checklist trước khi output code

- [ ] Code có dễ đọc không?
- [ ] Có duplicate không?
- [ ] Tên biến rõ nghĩa chưa? (snake_case cho biến/hàm)
- [ ] Có thể test được không?
- [ ] Có dễ mở rộng không?
- [ ] Comment đầy đủ chưa?

---

## 📌 Philosophy

> "Code is written once but read many times."

