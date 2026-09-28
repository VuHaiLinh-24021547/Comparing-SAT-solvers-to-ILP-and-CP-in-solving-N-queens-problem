from pysat.card import CardEnc, EncType
from pysat.solvers import Glucose3
import time
import math
import threading

def get_variable(n):
    return [[row * n + column + 1 for column in range(n)] for row in range(n)]

def solve_n_queens(n, encoding, timeout=120.0):
    start_time = time.time()
    solver = Glucose3()
    top_id = n * n
    variables = get_variable(n)

    def commander_encoding(variables, is_EO):
        nonlocal top_id
        m = len(variables)

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

            for x in group:
                solver.add_clause([c_i, -x])

    def sat_encoding(variables, is_EO):
        if encoding == "EncType.commander":
            commander_encoding(variables, is_EO)
            return

        EncType_mapping = {
            "EncType.bitwise": EncType.bitwise,
            "EncType.seqcounter": EncType.seqcounter,
        }

        nonlocal top_id

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

    # Solve
    solved = solver.solve()

    # Cancel timer if solving finished before timeout
    timer.cancel()
    elapsed = round(time.time() - start_time, 6)

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
    #     # for r in range(n):
    #     #     row = ["Q" if variables[r][c] in model else "." for c in range(n)]
    #     #     solution.append(" ".join(row))

    #     end_time = time.time()
    #     times.append(round(end_time - start_time, 6))

    #     # return "\n".join(solution)
    #     return "Solution found"

    # return "No solution"

times = []
grid_sizes = [1331]

#pairwise, bitwise, seqcounter, commander
encoding = "EncType.commander"
for grid_size in grid_sizes:
    solution = solve_n_queens(grid_size, encoding)
    print(f"Grid size: {grid_size}")
    print(solution)
print(times)