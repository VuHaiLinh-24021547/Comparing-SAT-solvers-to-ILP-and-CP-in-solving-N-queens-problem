from docplex.mp.model import Model

def solve_n_queens_mip(n):
    model = Model(name="N-Queens-MIP")

    x = model.binary_var_matrix(range(n), range(n), name="x")

    for i in range(n):
        model.add_constraint(model.sum(x[i, j] for j in range(n)) == 1, ctname=f"row_{i}")

    for j in range(n):
        model.add_constraint(model.sum(x[i, j] for i in range(n)) == 1, ctname=f"col_{j}")

    for i in range(n - 1):
        model.add_constraint(model.sum(x[i + j, j] for j in range(n - i)) <= 1, ctname=f"diagonal_{i - j}")

    for j in range(1, n - 1):
        model.add_constraint(model.sum(x[i, j + i] for i in range(n - j)) <= 1, ctname=f"diagonal_{i - j}")

    for i in range(n - 1):
        model.add_constraint(model.sum(x[i + j, n - 1 - j] for j in range(n - i)) <= 1, ctname=f"diagonal_{i + j}")

    for j in range(1, n - 1):
        model.add_constraint(model.sum(x[i, n - 1 - (i + j)] for i in range(n - j)) <= 1, ctname=f"diagonal_{i + j}")

    solution = model.solve()

    if solution:
        print("Found solution")
    else:
        print("No solution")

solve_n_queens_mip(33)