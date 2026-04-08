# 🧠 Coding Rules for AI Agent

## 🎯 Mục tiêu
Tạo code:
- Dễ đọc
- Dễ maintain
- Dễ mở rộng
- Ít bug
- Có structure rõ ràng
- comment chi tiết trong từng file code

---

## 1. 🧱 Nguyên tắc chung

- Luôn ưu tiên **readability hơn cleverness**
- Code phải **self-explanatory**, comment chi tiết
- Tránh viết code "hack", "tạm bợ"
- Mỗi file / function chỉ nên có **1 trách nhiệm chính (Single Responsibility)**

---

## 2. 🏷️ Naming Convention

### Biến / Hàm
- Dùng **camelCase**
- Tên phải có nghĩa rõ ràng

```js
// ❌ Bad
let x = getData()

// ✅ Good
let userList = fetchUsers()
Class / Component
Dùng PascalCase

js
class UserService {}
Constant
Dùng UPPER_SNAKE_CASE

js
const MAX_RETRY = 3
## 3. 📦 Structure & Organization
Tách file theo feature / module

Không để file quá 300-500 dòng

Mỗi folder có trách nhiệm rõ ràng

text
src/
  ├── services/
  ├── controllers/
  ├── models/
  ├── utils/
## 4. 🔧 Function Design
Hàm nên:

Ngắn (≤ 30 dòng)

Làm 1 việc duy nhất

Tránh nested quá sâu (max 2-3 levels)

js
// ❌ Bad
function process() {
  if (a) {
    if (b) {
      if (c) {
        ...
      }
    }
  }
}

// ✅ Good
function process() {
  if (!isValid()) return
  handleLogic()
}
## 5. 🧼 Clean Code Rules
Không duplicate code → dùng function / abstraction

Không hardcode → dùng config / constant

Tránh magic numbers

js
// ❌ Bad
if (user.age > 18)

// ✅ Good
const LEGAL_AGE = 18
if (user.age > LEGAL_AGE)
## 6. ⚠️ Error Handling
Không bỏ qua lỗi

Luôn handle rõ ràng

js
try {
  await fetchData()
} catch (error) {
  logger.error(error)
  throw new Error("Failed to fetch data")
}
## 7. 🧪 Testing Mindset
Code phải dễ test

Tránh phụ thuộc trực tiếp vào:

API

Database

Dùng dependency injection nếu có thể

## 8. 🔄 Reusability
Viết function/component có thể tái sử dụng

Tránh coupling chặt giữa các module

## 9. 🧾 Comment Rules
Chỉ comment khi cần thiết:

Giải thích "WHY", không phải "WHAT"

js
// ❌ Bad
// increase i by 1
i++

// ✅ Good
// retry mechanism to handle flaky API
retryCount++
## 10. 🚀 Performance
Không optimize sớm

Chỉ tối ưu khi:

Có bottleneck rõ ràng

Tránh loop lồng nhau nếu không cần thiết

## 11. 🔒 Security
Không hardcode:

API keys

Password

Validate input từ user

## 12. 🧩 Extensibility
Code phải dễ mở rộng:

Không sửa code cũ nhiều khi thêm feature mới

Ưu tiên:

Interface / abstraction

Config-driven design

## 13. 🤖 AI Agent Rules (Quan trọng)
Agent phải:

Không generate code dài nếu chưa cần

Luôn chia nhỏ problem

Luôn:

Hiểu requirement

Thiết kế structure

Viết code

Nếu không chắc:

→ hỏi lại thay vì đoán

## 14. ✅ Checklist trước khi output code
Code có dễ đọc không?

Có duplicate không?

Tên biến rõ nghĩa chưa?

Có thể test được không?

Có dễ mở rộng không?

📌 Philosophy
"Code is written once but read many times."