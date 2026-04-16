import os
import glob
from core.board import BoardModel  # Giả định đường dẫn tới class Board của bạn
from solvers.fol_kb import FOLKB
from solvers.forward import ForwardBacktrackSolver

def print_row(name, status, time, mem, steps):
    """Hàm hỗ trợ in các hàng cho bảng kết quả đẹp mắt"""
    print(f"| {name:<15} | {status:<10} | {time:<12.5f} | {mem:<12.4f} | {steps:<10} |")

def run_all_tests():
    input_folder = "Inputs"
    
    # Tìm tất cả file .txt trong thư mục Inputs và sắp xếp theo tên
    test_files = glob.glob(os.path.join(input_folder, "*.txt"))
    test_files.sort()

    if not test_files:
        print(f"❌ Không tìm thấy file .txt nào trong thư mục '{input_folder}'")
        return

    print("\n" + "="*73)
    print(f"🚀 BẮT ĐẦU CHẠY TEST TRÊN {len(test_files)} FILES INPUT")
    print("="*73)
    
    # In Header của bảng
    print(f"| {'Tên File':<15} | {'Trạng thái':<10} | {'Thời gian (s)':<12} | {'Bộ nhớ (MB)':<12} | {'Suy luận':<10} |")
    print("-" * 73)

    for file_path in test_files:
        file_name = os.path.basename(file_path)
        
        try:
            # 1. Khởi tạo dữ liệu
            board = BoardModel()
            board.load_from_file(file_path) # Cần khớp với hàm đọc file của bạn
            
            kb = FOLKB()
            kb.generate_clauses_from_board(board) # Cần khớp với logic tạo clause của bạn
            
            solver = ForwardBacktrackSolver(kb)

            # 2. Giải bài toán
            is_solved = solver.solve()

            # 3. Lấy thông số từ hàm bạn vừa yêu cầu
            stats = solver.get_stats()

            # 4. In ra Terminal
            status_text = "✅ SOLVED" if is_solved else "❌ FAILED"
            print_row(
                file_name, 
                status_text, 
                stats["time_sec"], 
                stats["memory_mb"], 
                stats["inferences"]
            )

        except Exception as e:
            # Nếu có file lỗi (sai format, v.v.), bỏ qua và báo lỗi
            print_row(file_name, "⚠️ ERROR", 0.0, 0.0, 0)
            # print(f"Chi tiết lỗi: {e}")

    print("="*73)
    print("🎉 ĐÃ HOÀN THÀNH TOÀN BỘ BÀI TEST!\n")

if __name__ == "__main__":
    run_all_tests()