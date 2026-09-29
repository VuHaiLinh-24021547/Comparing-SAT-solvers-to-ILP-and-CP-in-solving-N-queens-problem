import gurobipy as gp
from gurobipy import GRB
import time

def solve_n_queens(n, times, time_limit=120):
    model = gp.Model("N-Queens")

    model.setParam('TimeLimit', time_limit)

    x = model.addVars(n, n, vtype=GRB.BINARY, name="x")

    model.addConstrs((x.sum(i, '*') == 1 for i in range(n)), name="row")
    model.addConstrs((x.sum('*', j) == 1 for j in range(n)), name="column")

    for i in range(n - 1):
        model.addConstr(
            gp.quicksum(x[i + k, k] for k in range(n - i)) <= 1,
            name=f"diag_maj_left_{i}"
        )

    for j in range(1, n - 1):
        model.addConstr(
            gp.quicksum(x[k, j + k] for k in range(n - j)) <= 1,
            name=f"diag_maj_top_{j}"
        )
        
    for i in range(n - 1):
        model.addConstr(
            gp.quicksum(x[i + k, n - 1 - k] for k in range(n - i)) <= 1,
            name=f"diag_min_right_{i}"
        )

    for j in range(1, n - 1):
        model.addConstr(
            gp.quicksum(x[k, n - 1 - j - k] for k in range(n - j)) <= 1,
            name=f"diag_min_top_{j}"
    )

    start_time = time.perf_counter()

    model.optimize()

    elasped = time.perf_counter() - start_time

    if model.status == GRB.OPTIMAL:
        times.append(elasped)
    elif model.status == GRB.TIME_LIMIT:
        print(f"Time limit of {time_limit} seconds reached")
    else:
        print(model.status)

grid_sizes = [500]
times = []

for grid_size in grid_sizes:
    solve_n_queens(grid_size, times)
