import gurobipy as gp
from gurobipy import GRB
import time

def solve_n_queens(n, times, time_limit=120):
    model = gp.Model("N-Queens")

    encoding_start = time.perf_counter()
    is_timeout = False

    x = model.addVars(n, n, vtype=GRB.BINARY, name="x")

    model.addConstrs((x.sum(i, '*') == 1 for i in range(n)), name="row")
    model.addConstrs((x.sum('*', j) == 1 for j in range(n)), name="column")

    for i in range(n - 1):
        if time.perf_counter() - encoding_start > time_limit:
            is_timeout = True
            break
        model.addConstr(
            gp.quicksum(x[i + k, k] for k in range(n - i)) <= 1,
            name=f"diag_maj_left_{i}"
        )

    if not is_timeout:
        for j in range(1, n - 1):
            if time.perf_counter() - encoding_start > time_limit:
                is_timeout = True
                break
            model.addConstr(
                gp.quicksum(x[k, j + k] for k in range(n - j)) <= 1,
                name=f"diag_maj_top_{j}"
            )

    if not is_timeout:
        for i in range(n - 1):
            if time.perf_counter() - encoding_start > time_limit:
                is_timeout = True
                break
            model.addConstr(
                gp.quicksum(x[i + k, n - 1 - k] for k in range(n - i)) <= 1,
                name=f"diag_min_right_{i}"
            )

    if not is_timeout:
        for j in range(1, n - 1):
            if time.perf_counter() - encoding_start > time_limit:
                is_timeout = True
                break
            model.addConstr(
                gp.quicksum(x[k, n - 1 - j - k] for k in range(n - j)) <= 1,
                name=f"diag_min_top_{j}"
            )

    encoding_time = round(time.perf_counter() - encoding_start, 6)
    print(f"Grid size: {n}")
    print(f"Encoding time: {encoding_time}s")

    if is_timeout or encoding_time >= time_limit:
        print(f"Solving time: >{time_limit}s (Timeout during encoding)")
        times.append(f">{time_limit}s (Timeout)")
        return "Timeout reached"

    remaining_time = max(0.0, time_limit - encoding_time)
    model.setParam('TimeLimit', remaining_time)

    start_time = time.perf_counter()
    model.optimize()
    solving_time = round(time.perf_counter() - start_time, 6)

    if model.status == GRB.OPTIMAL:
        print(f"Solving time: {solving_time}s")
        times.append(solving_time)
        return "Solution found"
    elif model.status == GRB.TIME_LIMIT:
        print(f"Solving time: >{time_limit}s (Timeout reached)")
        times.append(f">{time_limit}s (Timeout)")
        return "Timeout reached"
    else:
        print(f"Solving time: {solving_time}s (Status: {model.status})")
        return f"Status {model.status}"

if __name__ == "__main__":
    import sys
    grid_sizes = [500]
    time_limit = 120
    times = []

    if len(sys.argv) > 1:
        grid_sizes = [int(sys.argv[1])]
    if len(sys.argv) > 2:
        time_limit = float(sys.argv[2])

    for grid_size in grid_sizes:
        result = solve_n_queens(grid_size, times, time_limit=time_limit)
        print(result)
