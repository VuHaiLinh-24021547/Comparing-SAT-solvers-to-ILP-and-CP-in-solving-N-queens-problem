from pysat.card import CardEnc, EncType
from pysat.solvers import Glucose3
import time
import math
import threading
import sys

def get_variable(n):
    return [[row * n + column + 1 for column in range(n)] for row in range(n)]

def solve_n_queens(n, encoding, timeout=120.0):
    solver = Glucose3()
    top_id = n * n
    variables = get_variable(n)

    def product_encoding(variables, is_EO):
        nonlocal top_id
        m = len(variables)

        if m <= 1:
            if m == 1 and is_EO:
                solver.add_clause([variables[0]])
            return

        p = math.ceil(math.sqrt(m))
        q = math.ceil(m / p)

        row_variables = [top_id + i + 1 for i in range(p)]
        top_id += p
        column_variables = [top_id + i + 1 for i in range(q)]
        top_id += q

        cnf_row = CardEnc.atmost(lits=row_variables, bound=1, top_id=top_id, encoding=EncType.pairwise)
        solver.append_formula(cnf_row.clauses)
        top_id = max(top_id, cnf_row.nv)

        cnf_col = CardEnc.atmost(lits=column_variables, bound=1, top_id=top_id, encoding=EncType.pairwise)
        solver.append_formula(cnf_col.clauses)
        top_id = max(top_id, cnf_col.nv)

        for idx in range(len(variables)):
            row_id = idx // q
            col_id = idx % q

            solver.add_clause([-variables[idx], row_variables[row_id]])
            solver.add_clause([-variables[idx], column_variables[col_id]])

        if (is_EO):
            solver.add_clause(variables)

    def commander_encoding(variables, is_EO):
        nonlocal top_id
        m = len(variables)

        if m <= 1:
            if m == 1 and is_EO:
                solver.add_clause([variables[0]])
            return

        g = math.ceil(math.sqrt(m))
        commanders = [top_id + i + 1 for i in range(g)]
        top_id += g

        if is_EO:
            cnf = CardEnc.equals(lits=commanders, bound=1, top_id=top_id, encoding=EncType.pairwise)        
        else:
            cnf = CardEnc.atmost(lits=commanders, bound=1, top_id=top_id, encoding=EncType.pairwise)

        top_id = max(top_id, cnf.nv)
        solver.append_formula(cnf.clauses)

        k = math.ceil(m / g)
        for i in range(g):
            group = variables[i * k: i * k + k]
            if not group:
                continue
            c_i = commanders[i]

            if len(group) > 1:
                cnf_group = CardEnc.atmost(lits=group + [-c_i], bound=1, top_id=top_id, encoding=EncType.pairwise)
                top_id = max(top_id, cnf_group.nv)
                solver.append_formula(cnf_group.clauses)

            solver.add_clause([-c_i] + group)

    def sat_encoding(variables, is_EO):
        nonlocal top_id
        m = len(variables)

        EncType_mapping = {
            "EncType.pairwise": EncType.pairwise,
            "EncType.bitwise": EncType.bitwise,
            "EncType.seqcounter": EncType.seqcounter,
        }

        if m <= 1:
            if m == 1 and is_EO:
                solver.add_clause([variables[0]])
            return

        if m <= 25:
            if is_EO:
                cnf = CardEnc.equals(lits=variables, bound=1, top_id=top_id, encoding=EncType.pairwise)
            else:
                cnf = CardEnc.atmost(lits=variables, bound=1, top_id=top_id, encoding=EncType.pairwise)
            top_id = max(top_id, cnf.nv)
            solver.append_formula(cnf.clauses)

            return

        if encoding == "EncType.commander":
            commander_encoding(variables, is_EO)
            return

        if encoding == "EncType.product":
            product_encoding(variables, is_EO)
            return

        if is_EO:
            cnf = CardEnc.equals(lits=variables, bound=1, top_id=top_id, encoding=EncType_mapping.get(encoding))
        else:
            cnf = CardEnc.atmost(lits=variables, bound=1, top_id=top_id, encoding=EncType_mapping.get(encoding))
        top_id = max(top_id, cnf.nv)
        solver.append_formula(cnf.clauses)
        
    for row in range(n):
        row_variables = variables[row]
        sat_encoding(row_variables, is_EO=True)

    for column in range(n):
        column_variables = [variables[row][column] for row in range(n)]
        sat_encoding(column_variables, is_EO=True)

    for row in range(n - 1):
        diagonal_variables = [variables[row + column][column] for column in range(n - row)]
        sat_encoding(diagonal_variables, is_EO=False)

    for column in range(1, n - 1):
        diagonal_variables = [variables[row][column + row] for row in range(n - column)]
        sat_encoding(diagonal_variables, is_EO=False)

    for row in range(n - 1):
        diagonal_variables = [variables[row + column][n - 1 - column] for column in range(n - row)]
        sat_encoding(diagonal_variables, is_EO=False)

    for column in range(1, n - 1):
        diagonal_variables = [variables[row][n - 1 - (column + row)] for row in range(n - column)]
        sat_encoding(diagonal_variables, is_EO=False)

    is_timeout = False
    def interrupt_solver():
        nonlocal is_timeout
        is_timeout = True
        solver.interrupt()  # Tells Glucose3 to halt immediately

    # Start timer thread
    timer = threading.Timer(timeout, interrupt_solver)
    timer.start()
    start_time = time.perf_counter()

    # Solve
    solved = solver.solve()

    # Cancel timer if solving finished before timeout
    timer.cancel()
    elapsed = round(time.perf_counter() - start_time, 6)

    if is_timeout:
        times.append(f">{timeout}s (Timeout)")
        return "Timeout reached"
    elif solved:
        times.append(elapsed)
        return "Solution found"
    else:
        times.append(elapsed)
        return "No solution"

    # if solved:
    #     model = set(solver.get_model())
    #     solution = []
    #     for r in range(n):
    #         row = ["Q" if variables[r][c] in model else "." for c in range(n)]
    #         solution.append(" ".join(row))

    #     end_time = time.time()
    #     times.append(round(end_time - start_time, 6))

    #     return "\n".join(solution)
        
    # return "No solution"

times = []
grid_sizes = [1000]

#pairwise, bitwise, seqcounter, commander, product
encoding = "EncType.product"

#choose encoding from terminal input
if len(sys.argv) > 1:
    encoding = sys.argv[1]

for grid_size in grid_sizes:
    solution = solve_n_queens(grid_size, encoding)
    print(f"Grid size: {grid_size}")
    print(solution)
print(times)