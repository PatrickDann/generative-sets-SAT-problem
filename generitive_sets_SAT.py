from pysat.formula import CNF
from pysat.solvers import Minisat22
import itertools

def encode_sat_problem(U, P0, R0, r):
    n = len(U)
    
    def add_initial_conditions(solver, P, R):
        for i in range(n):
            solver.add_clause([P[i], R[i]])        # P[i] or R[i]
            solver.add_clause([-P[i], -R[i]])      # not(P[i] and R[i])

    def add_operation_clauses(solver, P_prev, R_prev, A):
        for size in range(1, r + 1):
            for combination in itertools.combinations(range(n), size):
                clause = [A[i] for i in combination if U[i] in R_prev]
                if clause:
                    solver.add_clause(clause)

    def remove_operation_clauses(solver, P_prev, A):
        for size in range(1, r + 1):
            for combination in itertools.combinations(range(n), size):
                clause = [-A[i] for i in combination if U[i] in P_prev]
                if clause:
                    solver.add_clause(clause)

    def swap_operation_clauses(solver, P_prev, R_prev, A):
        for size in range(1, r + 1):
            for combination_r in itertools.combinations(range(n), size):
                for combination_p in itertools.combinations(range(n), size):
                    for i, j in zip(combination_r, combination_p):
                        if U[i] in R_prev and U[j] in P_prev:
                            solver.add_clause([-R_prev[i], -P_prev[j], A[i], -A[j]])

    def ensure_disjoint_sets(solver, A_sets):
        for A_i in A_sets:
            for A_j in A_sets:
                if A_i != A_j:
                    for i in range(n):
                        solver.add_clause([-A_i[i], -A_j[i]])

    def ensure_path(solver, Z, P_next):
        for z in Z:
            solver.add_clause([P_next[z]])

    def ensure_size_constraint(solver, P_prev, P_next):
        # Ensure size constraint: |P_prev| = |P_next|
        for i in range(n):
            solver.add_clause([P_prev[i], -P_next[i]])  # P_prev[i] => P_next[i]
            solver.add_clause([-P_prev[i], P_next[i]])  # not P_prev[i] => not P_next[i]

    def generate_next_state(solver, P_prev, R_prev, A_prev, step):
        A_vars = [i + 1 + (2 + step) * n for i in range(n)]
        P_next_vars = [i + 1 + (3 + step) * n for i in range(n)]
        R_next_vars = [i + 1 + (4 + step) * n for i in range(n)]
        
        # Add operations
        add_operation_clauses(solver, P_prev, R_prev, A_vars)
        remove_operation_clauses(solver, P_prev, A_vars)
        swap_operation_clauses(solver, P_prev, R_prev, A_vars)
        
        # Ensuring Z is a subset of P_next
        Z = {i for i in range(n) if U[i] in P_prev or U[i] in R_prev}
        ensure_path(solver, Z, P_next_vars)
        
        # Ensuring the size constraint
        ensure_size_constraint(solver, P_prev, P_next_vars)
        
        return A_vars, P_next_vars, R_next_vars

    # Initialize the first solver
    solver = Minisat22()
    P0_vars = [i + 1 for i in range(n)]
    R0_vars = [i + 1 + n for i in range(n)]
    
    # Add initial conditions
    add_initial_conditions(solver, P0_vars, R0_vars)
    
    # Start with P0 and R0
    P_prev = P0_vars
    R_prev = R0_vars
    
    # Generate A1, Z1, P1 with operations on P0
    A1_vars, P1_vars, R1_vars = generate_next_state(solver, P_prev, R_prev, None, 0)
    
    # Perform operations on P1 while ensuring Z1 is a subset of P1 and P2 is not the same size as P1
    A2_vars, P2_vars, R2_vars = generate_next_state(solver, P1_vars, R1_vars, A1_vars, 1)
    
    # Ensure A2 is disjoint from A1
    ensure_disjoint_sets(solver, [A1_vars, A2_vars])
    
    # Check satisfiability
    is_satisfiable = solver.solve()
    
    return is_satisfiable, P0_vars, R0_vars, A1_vars, A2_vars

def test_sat(U, P0, R0, r):
    is_satisfiable, P0_vars, R0_vars, A1_vars, A2_vars = encode_sat_problem(U, P0, R0, r)
    if is_satisfiable:
        print("The SAT problem is satisfiable. The conditions hold.")
    else:
        print("The SAT problem is not satisfiable. The conditions do not hold.")

U = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
P0 = [1, 2, 3, 4, 5]
R0 = [6, 7, 8, 9, 10]
r = 2

test_sat(U, P0, R0, r)