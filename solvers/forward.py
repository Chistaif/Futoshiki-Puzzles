from collections import deque

class ForwardChainingSolver:
    def __init__(self, cnf_clauses, initial_facts):
        """
        Khởi tạo bộ giải Forward Chaining.
        :param cnf_clauses: Danh sách các mệnh đề (clauses) từ FOL_KB. 
                            Mỗi mệnh đề là một list/tuple các literals.
                            VD: [('V_0_0_1', 'V_0_0_2'), ('-V_0_0_1', '-V_0_1_1')]
        :param initial_facts: Các sự kiện ban đầu (các ô đã có sẵn số).
                            VD: ['V_0_0_4', 'V_1_2_3']
        """
        # Copy lại KB để không làm hỏng dữ liệu gốc khi rút gọn
        self.clauses = [list(c) for c in cnf_clauses]

        # Hàng đợi chứa các sự kiện chắc chắn đúng (Agenda)
        self.agenda = deque(initial_facts)

        # Dictionary lưu kết quả suy diễn (Model): literal -> True
        self.model = {}

        # Khởi tạo thêm các unit clause từ KB để suy diễn tiến đúng cho các clause đơn
        self._enqueue_unit_clauses()

    def _enqueue_unit_clauses(self):
        for clause in self.clauses:
            if len(clause) == 1:
                literal = clause[0]
                if literal not in self.agenda and literal not in self.model:
                    self.agenda.append(literal)

    def solve(self):
        """
        Thực thi thuật toán suy diễn tiến.
        :return: model (dict) nếu tìm được nghiệm, False nếu KB chứa mâu thuẫn.
        """
        while self.agenda:
            # Lấy sự kiện đầu tiên ra khỏi hàng đợi
            p = self.agenda.popleft()
            
            # Nếu phủ định của p đã nằm trong model -> Xảy ra mâu thuẫn (Ví dụ: vừa có V_0_0_1 vừa có -V_0_0_1)
            if self._negate(p) in self.model:
                return False 
                
            if p not in self.model:
                # Đánh dấu sự kiện này là đúng
                self.model[p] = True
                
                new_clauses = []
                for clause in self.clauses:
                    # 1. Nếu p có trong mệnh đề -> Mệnh đề này đã luôn đúng (True), có thể loại bỏ khỏi KB
                    if p in clause:
                        continue
                    
                    # 2. Nếu phủ định của p có trong mệnh đề -> Literal này sai, xóa nó khỏi mệnh đề
                    neg_p = self._negate(p)
                    if neg_p in clause:
                        clause.remove(neg_p)
                        
                    # 3. Mâu thuẫn: Nếu mệnh đề bị xóa hết sạch các phần tử (rỗng) -> Không thể thỏa mãn
                    if len(clause) == 0:
                        return False
                        
                    # 4. Suy diễn: Nếu mệnh đề chỉ còn đúng 1 phần tử -> Phần tử đó chắc chắn đúng
                    if len(clause) == 1:
                        new_fact = clause[0]
                        if new_fact not in self.agenda and new_fact not in self.model:
                            self.agenda.append(new_fact)
                            
                    # Giữ lại các mệnh đề chưa được giải quyết xong
                    new_clauses.append(clause)
                
                # Cập nhật lại KB bằng các mệnh đề đã được rút gọn
                self.clauses = new_clauses
                
        # Trả về toàn bộ các sự kiện đã suy diễn được
        return self.model
        
    def _negate(self, literal):
        """Hàm phụ trợ lấy phủ định của một literal (VD: 'V_0_0_1' -> '-V_0_0_1')"""
        if literal.startswith('-'):
            return literal[1:]
        return '-' + literal