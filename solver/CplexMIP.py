import time
from docplex.mp.model import Model

def solve_n_queens_mip(n, time_limit=120):
    model = Model(name="N-Queens-MIP")

    encoding_start = time.perf_counter()
    is_timeout = False

    x = model.binary_var_matrix(range(n), range(n), name="x")

    for i in range(n):
        if time.perf_counter() - encoding_start > time_limit:
            is_timeout = True
            break
        model.add_constraint(model.sum(x[i, j] for j in range(n)) == 1, ctname=f"row_{i}")

    if not is_timeout:
        for j in range(n):
            if time.perf_counter() - encoding_start > time_limit:
                is_timeout = True
                break
            model.add_constraint(model.sum(x[i, j] for i in range(n)) == 1, ctname=f"col_{j}")

    if not is_timeout:
        for i in range(n - 1):
            if time.perf_counter() - encoding_start > time_limit:
                is_timeout = True
                break
            model.add_constraint(model.sum(x[i + j, j] for j in range(n - i)) <= 1, ctname=f"diagonal_{i - j}")

    if not is_timeout:
        for j in range(1, n - 1):
            if time.perf_counter() - encoding_start > time_limit:
                is_timeout = True
                break
            model.add_constraint(model.sum(x[i, j + i] for i in range(n - j)) <= 1, ctname=f"diagonal_{i - j}")

    if not is_timeout:
        for i in range(n - 1):
            if time.perf_counter() - encoding_start > time_limit:
                is_timeout = True
                break
            model.add_constraint(model.sum(x[i + j, n - 1 - j] for j in range(n - i)) <= 1, ctname=f"diagonal_{i + j}")

    if not is_timeout:
        for j in range(1, n - 1):
            if time.perf_counter() - encoding_start > time_limit:
                is_timeout = True
                break
            model.add_constraint(model.sum(x[i, n - 1 - (i + j)] for i in range(n - j)) <= 1, ctname=f"diagonal_{i + j}")

    encoding_time = round(time.perf_counter() - encoding_start, 6)
    print(f"Grid size: {n}")
    print(f"Encoding time: {encoding_time}s")

    if is_timeout or encoding_time >= time_limit:
        print(f"Solving time: >{time_limit}s (Timeout during encoding)")
        return "Timeout reached"

    remaining_time = max(0.0, time_limit - encoding_time)
    model.set_time_limit(remaining_time)

    solve_start = time.perf_counter()
    solution = model.solve(log_output=True)
    solving_time = round(time.perf_counter() - solve_start, 6)

    details = model.solve_details
    status_str = str(details.status).lower() if details else ""

    if solution:
        print(f"Solving time: {solving_time}s")
        print("Found solution")
        return "Solution found"
    elif "time" in status_str or solving_time >= remaining_time - 0.5:
        print(f"Solving time: >{time_limit}s (Timeout reached)")
        return "Timeout reached"
    else:
        print(f"Solving time: {solving_time}s")
        print("No solution")
        return "No solution"

if __name__ == "__main__":
    import sys
    n = 512
    time_limit = 120
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    if len(sys.argv) > 2:
        time_limit = float(sys.argv[2])
    result = solve_n_queens_mip(n, time_limit=time_limit)
    print(result)