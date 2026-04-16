_var_counter = 0

def is_variable(x):
    """
    Kiểm tra xem x có phải là biến logic hay không.
    Quy ước: Biến là chuỗi bắt đầu bằng chữ cái viết thường (vd: 'x', 'y', 'i', 'j').
    Hằng số là số nguyên hoặc chuỗi viết hoa (vd: 1, 2, 'A').
    """
    return isinstance(x, str) and x[0].islower()

def subst(theta, q):
    """
    Hàm SUBST: Áp dụng phép thế theta vào biểu thức q.
    """
    if isinstance(q, str):
        # Nếu q là biến và có trong theta, trả về giá trị thay thế. Nếu không, giữ nguyên.
        return theta.get(q, q)
    elif isinstance(q, (list, tuple)):
        # Nếu q là biểu thức phức hợp (VD: ('Val', 'i', 'j', 'v')), đệ quy áp dụng cho từng phần tử.
        return tuple(subst(theta, arg) for arg in q)
    else:
        # Nếu q là số hoặc kiểu dữ liệu khác, giữ nguyên
        return q

def occur_check(var, x, theta):
    """
    Kiểm tra xem biến 'var' có xuất hiện bên trong 'x' hay không để tránh vòng lặp đệ quy vô hạn.
    """
    if var == x:
        return True
    elif is_variable(x) and x in theta:
        return occur_check(var, theta[x], theta)
    elif isinstance(x, tuple):
        return any(occur_check(var, arg, theta) for arg in x)
    return False

def unify_var(var, x, theta):
    """Hàm hỗ trợ gán biến cho UNIFY."""
    if var in theta:
        return unify(theta[var], x, theta)
    elif x in theta:
        return unify(var, theta[x], theta)
    elif occur_check(var, x, theta):
        return "failure"
    else:
        new_theta = theta.copy()
        new_theta[var] = x
        return new_theta

def unify(x, y, theta=None):
    """
    Hàm UNIFY: Tìm Most General Unifier (MGU) của x và y.
    Trả về một dictionary chứa phép thế, hoặc chuỗi "failure" nếu không thể hợp nhất.
    """
    if theta is None:
        theta = {}

    if theta == "failure":
        return "failure"
    elif x == y:
        return theta
    elif is_variable(x):
        return unify_var(x, y, theta)
    elif is_variable(y):
        return unify_var(y, x, theta)
    elif isinstance(x, tuple) and isinstance(y, tuple):
        # Hợp nhất 2 tuple: hợp nhất phần tử đầu tiên, sau đó dùng kết quả để hợp nhất phần còn lại
        if len(x) != len(y):
            return "failure"
        return unify(x[1:], y[1:], unify(x[0], y[0], theta))
    elif isinstance(x, list) and isinstance(y, list):
        if len(x) != len(y):
            return "failure"
        return unify(x[1:], y[1:], unify(x[0], y[0], theta))
    else:
        return "failure"

def standardize_variables(rule):
    """
    Hàm STANDARDIZE-VARIABLES: Đổi tên các biến trong một luật để đảm bảo 
    các luật có không gian biến độc lập.
    Đầu vào 'rule' có dạng: (antecedents, consequent)
    """
    global _var_counter
    _var_counter += 1
    suffix = f"_{_var_counter}"  # Ví dụ: _1, _2, _3
    
    variables = set()
    
    # Hàm đệ quy con để tìm tất cả các biến logic có trong biểu thức
    def find_vars(expr):
        if is_variable(expr):
            variables.add(expr)
        # Hỗ trợ quét cả tuple và list
        elif isinstance(expr, (tuple, list)):
            # Bỏ qua phần tử đầu tiên (thường là tên Vị từ như 'Val', 'Less')
            # Quét đệ quy các tham số còn lại
            for arg in expr[1:]: 
                find_vars(arg)
                
    # Giải nén rule thành 2 phần rõ ràng để tránh nhầm lẫn index
    antecedents, consequent = rule
                
    # 1. Quét tìm tất cả các biến trong vế trái (antecedents)
    for premise in antecedents: 
        find_vars(premise)
        
    # 2. Quét tìm tất cả các biến trong vế phải (consequent)
    find_vars(consequent)
    
    # 3. Tạo tập phép thế theta để đổi tên. Ví dụ: {'x': 'x_1', 'y': 'y_1'}
    theta = {v: f"{v}{suffix}" for v in variables}
    
    # 4. Áp dụng phép thế theta vào luật cũ để tạo ra luật mới
    new_antecedents = tuple(subst(theta, p) for p in antecedents)
    new_consequent = subst(theta, consequent)
    
    return (new_antecedents, new_consequent)