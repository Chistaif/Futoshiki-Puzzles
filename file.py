def readFile(fileName):
    with open(fileName, 'r') as f:
        line = f.readline().strip()
        if not line:
            return None
        
        n = int(line)

        matrix = []
        for _ in range(n):
            row = list(map(int, f.readline().split(', ')))
            matrix.append(row)

        Horizontal = []
        for _ in range(n):
            row = list(map(int, f.readline().split(', ')))
            Horizontal.append(row)

        Vertical = []
        for _ in range(n - 1):
            row = list(map(int, f.readline().split(', ')))
            Vertical.append(row)

    return n, matrix, Horizontal, Vertical
