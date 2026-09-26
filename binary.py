import math
from pysat.solvers import Glucose3

def generate_variable(n):
    return [[i * n + j + 1 for j in range(n)] for i in range(n)]

def generate_binary_combinations(n):
    binary_combinations = []
    for i in range(1 << n):
        binary_combinations.append(format(i, '0' + str(n) + 'b'))
    return binary_combinations

def binary_encoding(clauses, target, new_variables):
    for i in range(len(new_variables)):
        clauses.append([-target, new_variables[i]])

# each row, column and diagonal has new variable 
def generate_new_variable(end, length):
    return [i for i in range(end + 1, end + math.ceil(math.log2(length)) + 1)]

def at_most_one(clauses, variables, new_variables):
    temp_new_variables = generate_new_variable(n ** 2 + len(new_variables), len(variables))
    new_variables += temp_new_variables

    binary_combinations = generate_binary_combinations(len(temp_new_variables))

    for i in range(len(variables)):
        combination = binary_combinations[i]
        temp_literals = []
        for j in range(len(combination)):
            if combination[j] == '1':
                temp_literals.append(temp_new_variables[j])
            else:
                temp_literals.append(-temp_new_variables[j])
        binary_encoding(clauses, variables[i], temp_literals)

def at_exactly_one(clauses, variables, new_variables):
    at_most_one(clauses, variables, new_variables)
    clauses.append(variables)

def generate_clauses(n, variables):
    clauses = []
    new_variables = []

    # exactly one in each row
    for i in range(n):
        at_exactly_one(clauses, variables[i], new_variables)

    # exactly one in each column
    for j in range(n):
        column_variables = [variables[i][j] for i in range(n)]
        at_exactly_one(clauses, column_variables, new_variables)

    for i in range(n - 1):
        diagonal_variables = []
        # append lower half of the diagonal
        for j in range(n - i):
            diagonal_variables.append(variables[i + j][j])
        at_most_one(clauses, diagonal_variables, new_variables)

    for j in range(1, n - 1):
        diagonal_variables = []
        # append upper half of the diagonal
        for i in range(n - j):
            diagonal_variables.append(variables[i][j + i])
        at_most_one(clauses, diagonal_variables, new_variables)

    for i in range(n - 1):
        counter_diagonal_variables = []
        # append lower half of the counter diagonal
        for j in range(n - i):
            counter_diagonal_variables.append(variables[i + j][n - 1 - j])
        at_most_one(clauses, counter_diagonal_variables, new_variables)

    for j in range(1, n - 1):
        counter_diagonal_variables = []
        # append upper half of the counter diagonal
        for i in range(n - j):
            counter_diagonal_variables.append(variables[i][n - 1 - (j + i)])
        at_most_one(clauses, counter_diagonal_variables, new_variables)

    return clauses

def solve_n_queens(n):
    variables = generate_variable(n)
    clauses = generate_clauses(n, variables)

    solver = Glucose3()
    for clause in clauses:
        solver.add_clause(clause)

    if solver.solve():
        model = solver.get_model()
        return [[int(model[i * n + j] > 0) for j in range(n)] for i in range(n)]
    else:
        return None

def print_solution(solution):
    if solution is None:
        print("No solution found.")
    else:
        for row in solution:
            print(" ".join("Q" if cell else "." for cell in row))

n = 512
solution = solve_n_queens(n)
print_solution(solution)