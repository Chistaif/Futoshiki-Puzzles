_var_counter = 0


def is_variable(x):
    """
    Kiá»ƒm tra xem x cÃ³ pháº£i lÃ  biáº¿n logic hay khÃ´ng.
    Quy Æ°á»›c: Biáº¿n lÃ  chuá»—i báº¯t Ä‘áº§u báº±ng chá»¯ cÃ¡i viáº¿t thÆ°á»ng (vd: 'x', 'y', 'i', 'j').
    Háº±ng sá»‘ lÃ  sá»‘ nguyÃªn hoáº·c chuá»—i viáº¿t hoa (vd: 1, 2, 'A').
    """
    return isinstance(x, str) and x[0].islower()


def subst(theta, q):
    """
    HÃ m SUBST: Ãp dá»¥ng phÃ©p tháº¿ theta vÃ o biá»ƒu thá»©c q.
    """
    if isinstance(q, str):
        # Náº¿u q lÃ  biáº¿n vÃ  cÃ³ trong theta, tráº£ vá» giÃ¡ trá»‹ thay tháº¿. Náº¿u khÃ´ng, giá»¯ nguyÃªn.
        return theta.get(q, q)
    elif isinstance(q, (list, tuple)):
        # Náº¿u q lÃ  biá»ƒu thá»©c phá»©c há»£p (VD: ('Val', 'i', 'j', 'v')), Ä‘á»‡ quy Ã¡p dá»¥ng cho tá»«ng pháº§n tá»­.
        return tuple(subst(theta, arg) for arg in q)
    else:
        # Náº¿u q lÃ  sá»‘ hoáº·c kiá»ƒu dá»¯ liá»‡u khÃ¡c, giá»¯ nguyÃªn
        return q


def occur_check(var, x, theta):
    """
    Kiá»ƒm tra xem biáº¿n 'var' cÃ³ xuáº¥t hiá»‡n bÃªn trong 'x' hay khÃ´ng Ä‘á»ƒ trÃ¡nh vÃ²ng láº·p Ä‘á»‡ quy vÃ´ háº¡n.
    """
    if var == x:
        return True
    elif is_variable(x) and x in theta:
        return occur_check(var, theta[x], theta)
    elif isinstance(x, tuple):
        return any(occur_check(var, arg, theta) for arg in x)
    return False


def unify_var(var, x, theta):
    """HÃ m há»— trá»£ gÃ¡n biáº¿n cho UNIFY."""
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
    HÃ m UNIFY: TÃ¬m Most General Unifier (MGU) cá»§a x vÃ  y.
    Tráº£ vá» má»™t dictionary chá»©a phÃ©p tháº¿, hoáº·c chuá»—i "failure" náº¿u khÃ´ng thá»ƒ há»£p nháº¥t.
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
        # Há»£p nháº¥t 2 tuple: há»£p nháº¥t pháº§n tá»­ Ä‘áº§u tiÃªn, sau Ä‘Ã³ dÃ¹ng káº¿t quáº£ Ä‘á»ƒ há»£p nháº¥t pháº§n cÃ²n láº¡i
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
    HÃ m STANDARDIZE-VARIABLES: Äá»•i tÃªn cÃ¡c biáº¿n trong má»™t luáº­t Ä‘á»ƒ Ä‘áº£m báº£o 
    cÃ¡c luáº­t cÃ³ khÃ´ng gian biáº¿n Ä‘á»™c láº­p.
    Äáº§u vÃ o 'rule' cÃ³ dáº¡ng: (antecedents, consequent)
    """
    global _var_counter
    _var_counter += 1
    suffix = f"_{_var_counter}"  # VÃ­ dá»¥: _1, _2, _3

    variables = set()

    # HÃ m Ä‘á»‡ quy con Ä‘á»ƒ tÃ¬m táº¥t cáº£ cÃ¡c biáº¿n logic cÃ³ trong biá»ƒu thá»©c
    def find_vars(expr):
        if is_variable(expr):
            variables.add(expr)
        # Há»— trá»£ quÃ©t cáº£ tuple vÃ  list
        elif isinstance(expr, (tuple, list)):
            # Bá» qua pháº§n tá»­ Ä‘áº§u tiÃªn (thÆ°á»ng lÃ  tÃªn Vá»‹ tá»« nhÆ° 'Val', 'Less')
            # QuÃ©t Ä‘á»‡ quy cÃ¡c tham sá»‘ cÃ²n láº¡i
            for arg in expr[1:]:
                find_vars(arg)

    # Giáº£i nÃ©n rule thÃ nh 2 pháº§n rÃµ rÃ ng Ä‘á»ƒ trÃ¡nh nháº§m láº«n index
    antecedents, consequent = rule

    # 1. QuÃ©t tÃ¬m táº¥t cáº£ cÃ¡c biáº¿n trong váº¿ trÃ¡i (antecedents)
    for premise in antecedents:
        find_vars(premise)

    # 2. QuÃ©t tÃ¬m táº¥t cáº£ cÃ¡c biáº¿n trong váº¿ pháº£i (consequent)
    find_vars(consequent)

    # 3. Táº¡o táº­p phÃ©p tháº¿ theta Ä‘á»ƒ Ä‘á»•i tÃªn. VÃ­ dá»¥: {'x': 'x_1', 'y': 'y_1'}
    theta = {v: f"{v}{suffix}" for v in variables}

    # 4. Ãp dá»¥ng phÃ©p tháº¿ theta vÃ o luáº­t cÅ© Ä‘á»ƒ táº¡o ra luáº­t má»›i
    new_antecedents = tuple(subst(theta, p) for p in antecedents)
    new_consequent = subst(theta, consequent)

    return (new_antecedents, new_consequent)

