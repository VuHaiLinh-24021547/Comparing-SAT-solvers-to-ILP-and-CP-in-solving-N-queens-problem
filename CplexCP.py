from docplex.cp.model import CpoModel

def solve_n_queens(n):
    mdl = CpoModel(name="N-Queens")

    Q = [mdl.integer_var(0, n - 1, name=f"Q_{i}") for i in range(n)]

    mdl.add(mdl.all_diff(Q))

    mdl.add(mdl.all_diff([Q[i] + i for i in range(n)]))

    mdl.add(mdl.all_diff([Q[i] - i for i in range(n)]))

    sol = mdl.solve()

    if sol:
        print("Found solution.")
    else:
        print("No solution found.")

solve_n_queens(101)