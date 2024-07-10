# generative-sets-SAT-problem

This repository contains a solution for encoding and solving a SAT problem using Python and the `pysat` library.

## Problem Description

Given:
- \( P_0 \): A set of numbers.
- \( R_0 \): A complement set of numbers.
- \( P_0 \cup R_0 = U \) and \( P_0 \cap R_0 = \emptyset \).

### Operations:
1. **Add** all combinations of up to \( r \) elements from \( R_0 \) to \( P_0 \).
2. **Remove** all combinations of up to \( r \) elements from \( P_0 \) to \( R_0 \).
3. **Swap** all combinations of up to \( r \) elements from \( R_0 \) to \( P_0 \).

We want to obtain \( P_1 \) (a new optional point) and \( Z_1 \) (the set of elements difference of \( P_0 \) and \( P_1 \)).

The goal is to prove that if we perform the operations on \( P_1 \), we will not find a set in \( A_1 \) from \( P_1 \) as long as \( Z_1 \) is kept in \( P_1 \) and we do not go back to the size of \( P_0 \).

## SAT Encoding

### Boolean Variables
For each element \( x \in U \):
- \( x_P \): Indicates whether \( x \) is in \( P_0 \).
- \( x_R \): Indicates whether \( x \) is in \( R_0 \).

For each element \( x \in U \) after an operation (i.e., for \( P_1 \)):
- \( x_{P1} \): Indicates whether \( x \) is in \( P_1 \).

### Clauses for Initial Conditions
1. Every element is either in \( P_0 \) or \( R_0 \):
   $$ (x_P \lor x_R) \quad \text{for each } x \in U $$
2. No element is in both \( P_0 \) and \( R_0 \):
   $$ \neg (x_P \land x_R) \quad \text{for each } x \in U $$

### Clauses for Operations

#### Add Operation
For adding combinations of up to \( r \) elements from \( R_0 \) to \( P_0 \):
1. **Add one element \( y \) from \( R_0 \) to \( P_0 \)**:
   $$ \neg y_R \lor y_{P1} \quad \text{for each } y \in R_0 $$
   This ensures that if \( y \) is not in \( R_0 \) (i.e., \( y_R \) is false), then \( y \) must be in \( P_1 \).

2. **Generalize for adding combinations of up to \( r \) elements**:
   For every subset \( S \subseteq R_0 \) where \( |S| \leq r \):
   $$ \bigvee_{y \in S} y_{P1} $$
   This ensures that at least one element in \( S \) is in \( P_1 \).

#### Remove Operation
For removing combinations of up to \( r \) elements from \( P_0 \) to \( R_0 \):
1. **Remove one element \( x \) from \( P_0 \) to \( R_0 \)**:
   $$ x_P \lor \neg x_{P1} \quad \text{for each } x \in P_0 $$
   This ensures that if \( x \) is in \( P_0 \) (i.e., \( x_P \) is true), then \( x \) must not be in \( P_1 \).

2. **Generalize for removing combinations of up to \( r \) elements**:
   For every subset \( S \subseteq P_0 \) where \( |S| \leq r \):
   $$ \bigvee_{x \in S} \neg x_{P1} $$
   This ensures that at least one element in \( S \) is not in \( P_1 \).

#### Swap Operation
For swapping combinations of up to \( r \) elements between \( P_0 \) and \( R_0 \):
1. **Swap one element \( y \) from \( R_0 \) with \( x \) from \( P_0 \)**:
   $$ (\neg y_R \lor \neg x_P \lor (y_{P1} \land \neg x_{P1})) \quad \text{for each } y \in R_0, x \in P_0 $$
   This ensures that if \( y \) is in \( R_0 \) and \( x \) is in \( P_0 \), then \( y \) must be in \( P_1 \) and \( x \) must not be in \( P_1 \).

2. **Generalize for swapping combinations of up to \( r \) elements**:
   For every subset \( S_1 \subseteq P_0 \) and \( S_2 \subseteq R_0 \) where \( |S_1| = |S_2| \leq r \):
   $$ \bigwedge_{y \in S_2, x \in S_1} (\neg y_R \lor \neg x_P \lor (y_{P1} \land \neg x_{P1})) $$
   This ensures that for every element in the subsets \( S_1 \) and \( S_2 \), the swap condition holds.

### Clauses for Ensuring the Conditions
1. **Ensuring \( Z_1 \) is kept in \( P_1 \)**:
   If \( Z_1 = (P_0 \setminus P_1) \cup (P_1 \setminus P_0) \):
   $$ \bigwedge_{z \in Z_1} z_{P1} $$
   This ensures that elements in \( Z_1 \) are in \( P_1 \).

2. **Ensuring the size constraint**:
   This requires counting the number of true variables in \( P_1 \) and ensuring it does not equal the number of true variables in \( P_0 \). 

