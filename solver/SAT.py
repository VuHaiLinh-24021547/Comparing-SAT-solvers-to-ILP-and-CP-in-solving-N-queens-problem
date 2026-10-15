from pysat.card import CardEnc, EncType
from pysat.solvers import Glucose4
import time
import math
import threading
import sys

def get_variable(n):
    return [[row * n + column + 1 for column in range(n)] for row in range(n)]

def solve_n_queens(n, encoding, timeout=120.0):
    solver = Glucose4()
    top_id = n * n
    variables = get_variable(n)
    is_timeout = False
    encoding_start = 0.0

    def product_encoding(variables, is_EO):
        nonlocal top_id
        m = len(variables)

        if m <= 1:
            if m == 1 and is_EO:
                solver.add_clause([variables[0]])
            return

        if m <= 10:
            if is_EO:
                cnf = CardEnc.equals(lits=variables, bound=1, top_id=top_id, encoding=EncType.pairwise)
            else:
                cnf = CardEnc.atmost(lits=variables, bound=1, top_id=top_id, encoding=EncType.pairwise)
            top_id = max(top_id, cnf.nv)
            solver.append_formula(cnf.clauses)
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
            solver.add_clause([-row_variables[row_id], -column_variables[col_id], variables[idx]])

        if is_EO:
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
            else:
                solver.add_clause([-group[0], c_i])

            solver.add_clause([-c_i] + group)

    def sat_encoding(variables, is_EO):
        nonlocal top_id, is_timeout
        if is_timeout or (time.perf_counter() - encoding_start > timeout):
            is_timeout = True
            return
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
        
    try:
        is_timeout = False
        def interrupt_solver():
            nonlocal is_timeout
            is_timeout = True
            solver.interrupt()

        timer = threading.Timer(timeout, interrupt_solver)
        timer.start()

        encoding_start = time.perf_counter()

        for row in range(n):
            if is_timeout or (time.perf_counter() - encoding_start > timeout):
                is_timeout = True
                break
            sat_encoding(variables[row], is_EO=True)

        if not is_timeout:
            for column in range(n):
                if is_timeout or (time.perf_counter() - encoding_start > timeout):
                    is_timeout = True
                    break
                sat_encoding([variables[row][column] for row in range(n)], is_EO=True)

        if not is_timeout:
            for row in range(n - 1):
                if is_timeout or (time.perf_counter() - encoding_start > timeout):
                    is_timeout = True
                    break
                sat_encoding([variables[row + column][column] for column in range(n - row)], is_EO=False)

        if not is_timeout:
            for column in range(1, n - 1):
                if is_timeout or (time.perf_counter() - encoding_start > timeout):
                    is_timeout = True
                    break
                sat_encoding([variables[row][column + row] for row in range(n - column)], is_EO=False)

        if not is_timeout:
            for row in range(n - 1):
                if is_timeout or (time.perf_counter() - encoding_start > timeout):
                    is_timeout = True
                    break
                sat_encoding([variables[row + column][n - 1 - column] for column in range(n - row)], is_EO=False)

        if not is_timeout:
            for column in range(1, n - 1):
                if is_timeout or (time.perf_counter() - encoding_start > timeout):
                    is_timeout = True
                    break
                sat_encoding([variables[row][n - 1 - (column + row)] for row in range(n - column)], is_EO=False)

        encoding_time = round(time.perf_counter() - encoding_start, 6)
        num_variables = top_id
        num_clauses = solver.nof_clauses()

        print(f"Grid size: {n}")
        print(f"Encoding stats: variables={num_variables}, clauses={num_clauses}, encoding_time={encoding_time}s")

        if is_timeout:
            timer.cancel()
            print(f"Solving time: >{timeout}s (Timeout during encoding)")
            return "Timeout reached"

        solve_start = time.perf_counter()
        solved = solver.solve()

        timer.cancel()
        solving_time = round(time.perf_counter() - solve_start, 6)

        if is_timeout:
            print(f"Solving time: >{timeout}s (Timeout)")
            return "Timeout reached"
        elif solved:
            print(f"Solving time: {solving_time}s")
            return "Solution found"
        else:
            print(f"Solving time: {solving_time}s")
            return "No solution"

    finally:
        solver.delete()

if __name__ == "__main__":
    grid_sizes = [512]

    encoding = "EncType.commander"

    if len(sys.argv) > 1:
        encoding = sys.argv[1]

    if len(sys.argv) > 2:
        grid_sizes = [int(sys.argv[2])]

    timeout = 120.0
    if len(sys.argv) > 3:
        timeout = float(sys.argv[3])

    for grid_size in grid_sizes:
        solution = solve_n_queens(grid_size, encoding, timeout=timeout)
        print(solution)