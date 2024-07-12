from pysat.formula import CNF
from pysat.solvers import Minisat22
import itertools

def encode_sat_problem(U, P0, R0, r):
    n = len(U)
    
    def add_initial_conditions(solver, P, R):
        """
        Add initial conditions to the solver.
        Each element should be either in P or in R, but not in both.
        """
        for i in range(n):
            solver.add_clause([P[i], R[i]])        # P[i] or R[i]
            solver.add_clause([-P[i], -R[i]])      # not(P[i] and R[i])

    def add_operation_clauses(solver, P_prev, R_prev, A):
        """
        Add clauses to the solver to handle 'add' operations.
        Allows adding up to 'r' elements from R_prev to P_prev.
        """
        for size in range(1, r + 1):
            for combination in itertools.combinations(range(n), size):
                clause = [A[i] for i in combination if P_prev[i] in R_prev]
                if clause:
                    solver.add_clause(clause)

    def remove_operation_clauses(solver, P_prev, A):
        """
        Add clauses to the solver to handle 'remove' operations.
        Allows removing up to 'r' elements from P_prev to R_prev.
        """
        for size in range(1, r + 1):
            for combination in itertools.combinations(range(n), size):
                clause = [-A[i] for i in combination if P_prev[i] in P_prev]
                if clause:
                    solver.add_clause(clause)

    def swap_operation_clauses(solver, P_prev, R_prev, A):
        """
        Add clauses to the solver to handle 'swap' operations.
        Allows swapping up to 'r' elements between P_prev and R_prev.
        """
        for size in range(1, r + 1):
            for combination_r in itertools.combinations(range(n), size):
                for combination_p in itertools.combinations(range(n), size):
                    for i, j in zip(combination_r, combination_p):
                        if R_prev[i] in R_prev and P_prev[j] in P_prev:
                            solver.add_clause([-R_prev[i], -P_prev[j], A[i], -A[j]])

    def ensure_non_disjoint_sets(solver, A1, A2):
        """
        Ensure that there is at least one common element between A1 and A2.
        """
        clause = []
        for i in range(n):
            clause.append(A1[i])
            clause.append(A2[i])
        solver.add_clause(clause)

    def ensure_path(solver, Z, P_next):
        """
        Ensure that Z (elements differing between P_prev and P_next) is a subset of P_next.
        """
        for z in Z:
            solver.add_clause([P_next[z]])

    def ensure_size_constraint(solver, P_prev, P_next):
        """
        Ensure that the size of P_next is not equal to the size of P_prev.
        """
        # by ensuring the number of true literals is different
        for i in range(len(P_prev)):
            for j in range(len(P_next)):
                if i != j:
                    solver.add_clause([-P_prev[i], P_next[j]])
                    solver.add_clause([P_prev[i], -P_next[j]])

    def generate_next_states(P_prev, R_prev):
        """
        Generate all possible next states by performing operations on P_prev and R_prev.
        """
        next_states = []
        for size in range(1, r + 1):
            # Generate states by adding elements from R_prev to P_prev
            for combination in itertools.combinations(range(n), size):
                if all(P_prev[i] in R_prev for i in combination):
                    new_P = P_prev + list(combination)
                    new_R = [x for x in R_prev if x not in combination]
                    next_states.append((new_P, new_R))
                
            # Generate states by removing elements from P_prev to R_prev
            for combination in itertools.combinations(range(n), size):
                if all(P_prev[i] in P_prev for i in combination):
                    new_P = [x for x in P_prev if x not in combination]
                    new_R = R_prev + list(combination)
                    next_states.append((new_P, new_R))
                
            # Generate states by swapping elements between P_prev and R_prev
            for combination_r in itertools.combinations(range(n), size):
                for combination_p in itertools.combinations(range(n), size):
                    if all(R_prev[i] in R_prev for i in combination_r) and all(P_prev[j] in P_prev for j in combination_p):
                        new_P = [x for x in P_prev if x not in combination_p] + list(combination_r)
                        new_R = [x for x in R_prev if x not in combination_r] + list(combination_p)
                        next_states.append((new_P, new_R))
                    
        return next_states

    def check_all_next_states(P_prev, R_prev):
        """
        Check all possible next states to ensure constraints.
        """
        next_states = generate_next_states(P_prev, R_prev)
        for P_next, R_next in next_states:
            if len(P_next) > n or len(R_next) > n:
                continue
            
            # Create a new solver for each next state
            with Minisat22() as local_solver:
                # Generate variables for the next state
                A_vars = [i + 1 + (2 + 1) * n for i in range(n)]
                P_next_vars = [i + 1 + (3 + 1) * n for i in range(n)]
                R_next_vars = [i + 1 + (4 + 1) * n for i in range(n)]
                
                # Apply operation clauses to the local solver
                add_operation_clauses(local_solver, P_prev, R_prev, A_vars)
                remove_operation_clauses(local_solver, P_prev, A_vars)
                swap_operation_clauses(local_solver, P_prev, R_prev, A_vars)
                
                # Ensure path and size constraints
                Z = {i for i in range(len(P_prev)) if (P_prev[i] != P_next[i])}
                ensure_path(local_solver, Z, P_next_vars)
                ensure_size_constraint(local_solver, P_prev, P_next_vars)
                
                # Ensure at least one common element between A_vars and P_next_vars
                ensure_non_disjoint_sets(local_solver, A_vars, P_next_vars)
                
                # Check satisfiability
                is_satisfiable = local_solver.solve()
                if is_satisfiable:
                    return True
        return False

    solver = Minisat22()
    P0_vars = [i + 1 for i in range(n)]
    R0_vars = [i + 1 + n for i in range(n)]
    
    # Ensure P0 and R0 do not overlap
    if set(P0) & set(R0):
        raise ValueError("P0 and R0 overlap, which is not allowed.")
    
    add_initial_conditions(solver, P0_vars, R0_vars)
    
    P_prev = list(range(1, n + 1))
    R_prev = list(range(n + 1, 2 * n + 1))
    
    # Check all possible next states for P1
    is_satisfiable = check_all_next_states(P_prev, R_prev)
    
    return is_satisfiable, P0_vars, R0_vars

def test_sat(U, P0, R0, r):
    try:
        is_satisfiable, P0_vars, R0_vars = encode_sat_problem(U, P0, R0, r)
        if is_satisfiable:
            print("The SAT problem is satisfiable. Non-disjoint sets exist.")
        else:
            print("The SAT problem is not satisfiable. No non-disjoint sets found.")
    except ValueError as e:
        print(f"Error: {e}")

# Example usage
U = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
P0 = [1, 2, 3, 4, 5]
R0 = [6, 7, 8, 9, 10]
r = 2

test_sat(U, P0, R0, r)



