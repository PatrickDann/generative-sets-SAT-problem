# generative-sets-SAT-problem

This repository contains a solution for encoding and solving a SAT problem using Python and the `pysat` library.

## Problem Description

Given:
- \( P_0 \): A set of numbers.
- \( R_0 \): A complement set of numbers.
- \( P_0 \cup R_0 = U \) and \( P_0 \cap R_0 = \emptyset \).

Operations:
- Add all combinations up to \( r \) elements from \( R_0 \) to \( P_0 \).
- Remove all combinations up to \( r \) elements from \( P_0 \) to \( R_0 \).
- Swap all combinations up to \( r \) elements from \( R_0 \) to \( P_0 \).

We want to obtain \( P_1 \) (a new optional point) and \( Z_1 \) (the set of elements difference of \( P_0 \) and \( P_1 \)).
The goal is to prove that if we perform the operations on \( P_1 \), we will not find a set in \( A_1 \) from \( P_1 \) as long as \( Z_1 \) is kept in \( P_1 \) and we do not go back to the size of \( P_0 \).

## SAT Encoding

The problem is encoded using Boolean variables and clauses to represent the add, remove, and swap operations.

- **Add Operation**: Add up to \( r \) elements from \( R_0 \) to \( P_0 \).
- **Remove Operation**: Remove up to \( r \) elements from \( P_0 \) to \( R_0 \).
- **Swap Operation**: Swap up to \( r \) elements between \( P_0 \) and \( R_0 \).

The resulting SAT problem is then solved using the `pysat` library to determine if the conditions hold.
