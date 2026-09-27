from pysat.card import CardEnc, EncType
from pysat.solvers import Glucose3

def solve_n_queens(n, encoding):
    solver = Glucose3()
    top_id = n * n

    def get_variable(row, col):
        return row * n + col + 1

    for row in range(n):
        row_variables = [get_variable(row, col) for col in range(n)]
        cnf = CardEnc.equals(lits=row_variables, bound=1, top_id=top_id, encoding=encoding)
        top_id = max(top_id, cnf.nv)
        solver.append_formula(cnf.clauses)

    for column in range(n):
        column_variables = [get_variable(row, column) for row in range(n)]
        cnf = CardEnc.equals(lits=column_variables, bound=1, top_id=top_id, encoding=encoding)
        top_id = max(top_id, cnf.nv)
        solver.append_formula(cnf.clauses)

    for row in range(n - 1):
        diagonal_variables = [get_variable(row + column, column) for column in range(n - row)]
        cnf = CardEnc.atmost(lits=diagonal_variables, bound=1, top_id=top_id, encoding=encoding)
        top_id = max(top_id, cnf.nv)
        solver.append_formula(cnf.clauses)

    for column in range(1, n - 1):
        diagonal_variables = [get_variable(row, column + row) for row in range(n - column)]
        cnf = CardEnc.atmost(lits=diagonal_variables, bound=1, top_id=top_id, encoding=encoding)
        top_id = max(top_id, cnf.nv)
        solver.append_formula(cnf.clauses)

    for row in range(n - 1):
        diagonal_variables = [get_variable(row + column, n - 1 - column) for column in range(n - row)]
        cnf = CardEnc.atmost(lits=diagonal_variables, bound=1, top_id=top_id, encoding=encoding)
        top_id = max(top_id, cnf.nv)
        solver.append_formula(cnf.clauses)

    for column in range(1, n - 1):
        diagonal_variables = [get_variable(row, n - 1 - (column + row)) for row in range(n - column)]
        cnf = CardEnc.atmost(lits=diagonal_variables, bound=1, top_id=top_id, encoding=encoding)
        top_id = max(top_id, cnf.nv)
        solver.append_formula(cnf.clauses)

    if solver.solve():
        model = set(solver.get_model())
        solution = []
        for r in range(n):
            row = ["Q" if get_variable(r, c) in model else "." for c in range(n)]
            solution.append(" ".join(row))
        return "\n".join(solution)
    return "No solution"

print(solve_n_queens(4, EncType.pairwise))