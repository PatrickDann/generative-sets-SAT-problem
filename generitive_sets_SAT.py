from pysat.formula import CNF
from pysat.solvers import Minisat22
import itertools

def encode_sat_problem(U, P0, R0, r):
    solver = Minisat22()
    n = len(U)
    
    # Create Boolean variables for P0, R0, P1
    P = [i + 1 for i in range(n)]
    R = [i + 1 + n for i in range(n)]
    P1 = [i + 1 + 2 * n for i in range(n)]

    # Initial conditions: each element is in either P0 or R0 but not both
    for i in range(n):
        solver.add_clause([P[i], R[i]])        # P[i] or R[i]
        solver.add_clause([-P[i], -R[i]])      # not (P[i] and R[i])

    # Define clauses for sets in A1
    A1_clauses = CNF()

    # Add operations: add up to r elements from R0 to P0
    for size in range(1, r + 1):
        for combination in itertools.combinations([i for i in range(n) if U[i] in R0], size):
            clause = [P[i] for i in combination]
            A1_clauses.append(clause)  # Ensure at least one in combination is in P

    # Remove operations: remove up to r elements from P0 to R0
    for size in range(1, r + 1):
        for combination in itertools.combinations([i for i in range(n) if U[i] in P0], size):
            clause = [-P[i] for i in combination]
            A1_clauses.append(clause)  # Ensure at least one in combination is not in P

    # Swap operations: swap up to r elements between P0 and R0
    for size in range(1, r + 1):
        for combination_r in itertools.combinations([i for i in range(n) if U[i] in R0], size):
            for combination_p in itertools.combinations([i for i in range(n) if U[i] in P0], size):
                for i, j in zip(combination_r, combination_p):
                    A1_clauses.append([-R[i], -P[j], P[i]])  # not(R[i] and P[j]) or P[i]
                    A1_clauses.append([-R[i], -P[j], -P[j]]) # not(R[i] and P[j]) or notP[j]

    # Apply A1 clauses to solver for P1
    for clause in A1_clauses:
        solver.add_clause(clause)

    # Ensuring Z1 is kept
    Z1 = set(P0).symmetric_difference(P1)
    for i in range(n):
        if U[i] in Z1:
            solver.add_clause([P1[i]])

    # Ensure size constraint: P1 should not revert to the size of P0
    size_P0 = len(P0)
    size_P1 = len(P1)
    if size_P0 == size_P1:
        solver.add_clause([0]) # ensures we do not have P1 of the same size as P0

    # Check satisfiability
    is_satisfiable = solver.solve()

    return is_satisfiable, P, R, P1

def test_sat(U, P0, R0, r):
    is_satisfiable, P, R, P1 = encode_sat_problem(U, P0, R0, r)
    if is_satisfiable:
        print("The SAT problem is satisfiable. The conditions hold.")
    else:
        print("The SAT problem is not satisfiable. The conditions do not hold.")

# Example usage
U = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
P0 = [1, 2, 3, 4, 5]
R0 = [6, 7, 8, 9, 10]
r = 2

test_sat(U, P0, R0, r)