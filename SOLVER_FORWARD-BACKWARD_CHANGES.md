# Tóm Tắt Thay Đổi Streaming Solver (Commit-Ready)

## What changed

### backward.py
- Thêm `StepCallback = Callable[[int, int, int], None]`.
- Cập nhật chữ ký hàm `solve(...)` để nhận `step_callback` (tùy chọn).
- Truyền `step_callback` xuyên suốt trong đệ quy `_backtrack(...)`.
- Emit step khi gán giá trị: `step_callback(i, j, v)`.
- Emit step khi quay lui (undo): `step_callback(i, j, 0)`.

### forward.py
- Thêm `StepCallback = Callable[[int, int, int], None]`.
- Cập nhật `solve(...)` để nhận `step_callback` (tùy chọn).
- Truyền callback vào `_dpll(...)` và `_propagate(...)`.
- Emit step khi literal dương được gán trong quá trình propagation.
- Emit step undo (`value = 0`) cho các gán dương bị rollback sau khi nhánh thử thất bại.
- Thêm helper decode literal dương sang ô bàn cờ `(row, col, value)` để map đúng step cho UI.
- Sửa luồng rẽ nhánh DPLL: không gán trước literal nhánh trực tiếp vào `model`; thay vào đó đẩy literal vào `agenda` để propagation xử lý gán + đơn giản hóa clause một cách nhất quán.

## Why changed
- Trước đó solver Backward/Forward chưa stream step tìm kiếm thực, nên animation UI có thể đứng yên hoặc nhảy thẳng tới trạng thái cuối.
- Luồng tích hợp UI cần chuỗi sự kiện tăng dần `(row, col, value)` để animate từng hành động của solver.
- Forward solver có lỗi đúng/sai ở phần rẽ nhánh DPLL: gán trực tiếp trước propagation có thể bỏ qua một số cập nhật clause cần thiết và dẫn đến kết quả sai/không hợp lệ.
- Chuẩn hóa cả hai solver theo cơ chế emit step qua callback giúp hành vi đồng nhất với các AI solver khác trong project.

## Impact on UI animation
- Animation bắt đầu ngay khi solver bắt đầu tìm kiếm, không phải đợi solve xong toàn bộ.
- Mỗi lần xuất hiện số trên bàn cờ tương ứng với một bước quyết định thật của solver.
- Hành động quay lui hiển thị rõ bằng việc xóa ô (`value = 0`), giúp thấy được quá trình thử-sai.
- Forward solver hiển thị các bước suy diễn theo propagation theo đúng thứ tự, giúp dễ hiểu cách DPLL hoạt động trong UI.
- Phản hồi solver liên tục hơn: queue nhận nhiều sự kiện nhỏ thay vì chỉ phát lại bàn cờ cuối.
- Cảm giác phản hồi của UI tốt hơn vì bàn cờ cập nhật trong lúc đang tính.
- Độ tin cậy hiển thị tăng lên: các bước animation bám sát logic tìm kiếm nội bộ và trạng thái nghiệm hợp lệ cuối cùng.
