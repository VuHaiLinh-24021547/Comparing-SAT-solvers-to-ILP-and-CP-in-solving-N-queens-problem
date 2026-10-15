import time
from docplex.cp.model import CpoModel
from docplex.cp.config import context

context.solver.agent = 'local'
context.solver.local.execfile = './ibm/ILOG/CPLEX_Studio222/cpoptimizer/bin/x86-64_linux/cpoptimizer'

def solve_n_queens(n, time_limit=120):
    encoding_start = time.perf_counter()

    mdl = CpoModel(name="N-Queens")

    Q = [mdl.integer_var(0, n - 1, name=f"Q_{i}") for i in range(n)]

    mdl.add(mdl.all_diff(Q))

    mdl.add(mdl.all_diff([Q[i] + i for i in range(n)]))

    mdl.add(mdl.all_diff([Q[i] - i for i in range(n)]))

    encoding_time = round(time.perf_counter() - encoding_start, 6)
    print(f"Grid size: {n}")
    print(f"Encoding time: {encoding_time}s")

    if encoding_time >= time_limit:
        print(f"Solving time: >{time_limit}s (Timeout during encoding)")
        return "Timeout reached"

    remaining_time = max(0.0, time_limit - encoding_time)

    solve_start = time.perf_counter()
    sol = mdl.solve(TimeLimit=remaining_time)
    solving_time = round(time.perf_counter() - solve_start, 6)

    if sol and sol.is_solution():
        print(f"Solving time: {solving_time}s")
        print("Found solution.")
        return "Solution found"
    elif (sol and hasattr(sol, 'get_solve_stop_status') and sol.get_solve_stop_status() == "TimeLimit") or solving_time >= remaining_time - 0.5:
        print(f"Solving time: >{time_limit}s (Timeout reached)")
        return "Timeout reached"
    else:
        print(f"Solving time: {solving_time}s")
        print("No solution found.")
        return "No solution"

if __name__ == "__main__":
    import sys
    n = 2048
    time_limit = 120
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    if len(sys.argv) > 2:
        time_limit = float(sys.argv[2])
    result = solve_n_queens(n, time_limit=time_limit)
    print(result)