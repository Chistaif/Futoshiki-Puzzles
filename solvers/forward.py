import time
import tracemalloc
from collections import defaultdict, deque
import copy

class ForwardBacktrackSolver:
    def __init__(self, kb):
        self.clauses = copy.deepcopy(kb.clauses)
        self.model = {}
        self.agenda = deque()
        self.literal_to_clauses = defaultdict(list)
        
        # Các biến lưu trữ thống kê
        self.inferences = 0 
        self.run_time = 0.0
        self.memory_usage = 0.0
        
        for clause in self.clauses:
            if len(clause) == 1:
                self.agenda.append(clause[0])
            else:
                for literal in clause:
                    self.literal_to_clauses[literal].append(clause)

    def _enqueue_unit_clauses(self):
        for clause in self.clauses:
            if len(clause) == 1:
                literal = clause[0]
                if literal not in self.agenda and literal not in self.model:
                    self.agenda.append(literal)

    def solve(self):
        """Hàm thực thi chính: Vừa giải vừa đo lường"""
        tracemalloc.start()
        start_time = time.perf_counter()

        # Chạy thuật toán
        is_solved = self._dpll()

        # Chốt số liệu
        end_time = time.perf_counter()
        current_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        self.run_time = end_time - start_time
        self.memory_usage = peak_mem / (1024 * 1024) # Chuyển sang MB

        return is_solved
    
    def get_stats(self):
        """Hàm trả về dữ liệu đo được cho UI hoặc Terminal gọi"""
        return {
            "time_sec": self.run_time,
            "memory_mb": self.memory_usage,
            "inferences": self.inferences
        }

    def _dpll(self):
        # Bước 1: Lan truyền hệ quả (Forward Chaining)
        if not self.propagate():
            return False # Nhánh này sinh mâu thuẫn, báo False để quay lui
            
        # Bước 2: Kiểm tra xem đã giải xong chưa
        unassigned_var = self._get_unassigned_variable()
        if unassigned_var is None:
            return True # Không còn biến nào để gán -> Đã tìm được Model hợp lệ!

        # Bước 3: BACKTRACKING - Bị đứng, bắt đầu đoán
        # Vì đây là đệ quy và các clause/model bị thay đổi inplace (list.remove),
        # ta BẮT BUỘC phải lưu lại trạng thái trước khi đi vào nhánh rẽ.
        saved_clauses = copy.deepcopy(self.clauses)
        saved_literal_to_clauses = copy.deepcopy(self.literal_to_clauses)
        saved_model = self.model.copy()
        
        # --- Nhánh 1: Đoán biến bằng True ---
        self.agenda.append(unassigned_var) # Nhét thử vào agenda
        if self._dpll():
            return True # Nhánh này đúng thì kết thúc luôn
            
        # --- Nhánh 2: Nếu nhánh 1 sai, phục hồi trạng thái và đoán biến bằng False ---
        # Khôi phục trạng thái cũ
        self.clauses = saved_clauses
        self.literal_to_clauses = saved_literal_to_clauses
        self.model = saved_model
        self.agenda.clear() # Dọn dẹp agenda
        
        # Ép biến đó bằng False (tức là neg_var bằng True)
        self.agenda.append(self._negate(unassigned_var))
        
        # Thử lại nhánh False, kết quả của nhánh này cũng là kết quả cuối cùng của node hiện tại
        return self._dpll()
        
        
    def _negate(self, literal):
        return -literal if isinstance(literal, int) else ('-' + literal[1:] if literal.startswith('-') else '-' + literal)
    
    def propagate(self):
        """Hàm này chỉ thực hiện Forward Chaining mà không cần suy diễn ngược (Backtracking)."""
        while self.agenda:
            p = self.agenda.popleft()
            self.inferences += 1
            
            if self._negate(p) in self.model:
                return False # Mâu thuẫn logic -> nhánh này vô nghiệm
                
            if p not in self.model:
                self.model[p] = True
                neg_p = self._negate(p)
                
                # CHỈ DUYỆT các mệnh đề chứa neg_p thay vì toàn bộ clauses
                clauses_to_check = self.literal_to_clauses[neg_p]
                for clause in clauses_to_check:
                    if neg_p in clause:
                        clause.remove(neg_p)
                        # Nếu mệnh đề rỗng -> mâu thuẫn
                        if len(clause) == 0:
                            return False
                        # Nếu mệnh đề chỉ còn 1 phần tử -> thành sự thật mới
                        if len(clause) == 1:
                            new_fact = clause[0]
                            if new_fact not in self.model and new_fact not in self.agenda:
                                self.agenda.append(new_fact)
                                
        return True # Trả về True nghĩa là chưa có mâu thuẫn (có thể chưa giải xong)
    
    def _get_unassigned_variable(self):
        """Hàm này tìm một literal bất kỳ trong các mệnh đề có độ dài > 1 để thử gán giá trị (Backtracking)."""
        # Tìm một literal bất kỳ trong các mệnh đề có độ dài > 1
        for clause in self.clauses:
            if len(clause) > 1: # Bỏ qua mệnh đề đã thỏa mãn hoặc trống
                for literal in clause:
                    # Chú ý: Cần kiểm tra biến gốc đã có trong model chưa (cả dạng khẳng định và phủ định)
                    pos_var = abs(literal) if isinstance(literal, int) else literal.replace('-', '')
                    neg_var = self._negate(pos_var)
                    if pos_var not in self.model and neg_var not in self.model:
                        return pos_var # Chọn một biến dương để thử
        return None