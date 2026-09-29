import time
from ortools.sat.python import cp_model

def n_queens_cp_sat(grid_size: int, times) -> None:
    model = cp_model.CpModel()

    queens = [model.new_int_var(0, grid_size - 1, f"x_{i}") for i in range(grid_size)]

    model.add_all_different(queens)

    model.add_all_different(queens[i] + i for i in range(grid_size))
    model.add_all_different(queens[i] - i for i in range(grid_size))

    solver = cp_model.CpSolver()
    solver.parameters.enumerate_all_solutions = False
    status = solver.solve(model)

    if status == cp_model.OPTIMAL or cp_model.FEASIBLE:
        times.append(solver.WallTime())
    else:
        print("no solution")

times = []
grid_sizes = [200]
for grid_size in grid_sizes:
    n_queens_cp_sat(grid_size, times)
print(times)