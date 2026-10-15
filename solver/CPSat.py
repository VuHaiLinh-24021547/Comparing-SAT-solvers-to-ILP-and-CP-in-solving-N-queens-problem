import time
from ortools.sat.python import cp_model

def n_queens_boolean_cpsat(n: int, time_limit: float = 120.0):
    model = cp_model.CpModel()

    encoding_start = time.perf_counter()
    is_timeout = False

    x = [[model.new_bool_var(f"x_{i}_{j}") for j in range(n)] for i in range(n)]

    for i in range(n):
        model.AddExactlyOne(x[i][j] for j in range(n))
        model.AddExactlyOne(x[j][i] for j in range(n))

    for k in range(-(n - 1), n):
        if time.perf_counter() - encoding_start > time_limit:
            is_timeout = True
            break
        diag = [x[i][j] for i in range(n) for j in range(n) if i - j == k]
        if len(diag) > 1:
            model.AddAtMostOne(diag)

    if not is_timeout:
        for k in range(2 * n - 1):
            if time.perf_counter() - encoding_start > time_limit:
                is_timeout = True
                break
            anti_diag = [x[i][j] for i in range(n) for j in range(n) if i + j == k]
            if len(anti_diag) > 1:
                model.AddAtMostOne(anti_diag)

    encoding_time = round(time.perf_counter() - encoding_start, 6)
    print(f"Grid size: {n}")
    print(f"Encoding time: {encoding_time}s")

    if is_timeout or encoding_time >= time_limit:
        print(f"Solving time: >{time_limit}s (Timeout during encoding)")
        return "Timeout reached"

    remaining_time = max(0.0, time_limit - encoding_time)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 0  # Use all available CPU cores
    solver.parameters.max_time_in_seconds = float(remaining_time)

    start = time.perf_counter()
    status = solver.solve(model)
    solving_time = round(time.perf_counter() - start, 6)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print(f"Solving time: {solving_time}s")
        print(f"Boolean CP-SAT solved N={n} in {solving_time}s (Solver WallTime: {solver.WallTime():.4f}s)")
        return "Solution found"
    elif status == cp_model.UNKNOWN or solving_time >= remaining_time - 0.5:
        print(f"Solving time: >{time_limit}s (Timeout reached)")
        return "Timeout reached"
    else:
        print(f"Solving time: {solving_time}s")
        print("No solution")
        return "No solution"

if __name__ == "__main__":
    import sys
    grid_sizes = [1024]
    time_limit = 120.0
    if len(sys.argv) > 1:
        grid_sizes = [int(sys.argv[1])]
    if len(sys.argv) > 2:
        time_limit = float(sys.argv[2])
    for grid_size in grid_sizes:
        result = n_queens_boolean_cpsat(grid_size, time_limit=time_limit)
        print(result)