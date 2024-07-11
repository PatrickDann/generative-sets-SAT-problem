# generative-sets-SAT-problem

This repository contains a solution for encoding and solving a SAT problem using Python and the `pysat` library.

## Problem Description

Given the initial conditions:
- \($ P_0 $ \): A set of numbers.
- \($ R_0 $ \): A complement set of numbers.
- \($ P_0 \cup R_0 = U $ \) and \($ P_0 \cap R_0 = \emptyset $ \).

### Operations:
1. **Add** all combinations of up to $ r $  elements from $ R_0 $  to $ P_0 $ .
2. **Remove** all combinations of up to $ r $  elements from $ P_0 $  to $ R_0 $ .
3. **Swap** all combinations of up to $ r $  elements from $ R_0 $  to $ P_0 $ .

We Perform operations (add, remove, swap) to generate new sets $ A_{i+1} $ from $ P_i $. Then
we select an optimal set $ P_{i+1} $ from $ A_{I+1} $ and define $ Z_{i+1} $ as the symmetric difference between $ P_i $ and $ P_{i+1} $.
To ensure disjointness between each iteration of $ A_i's $ we maintain the path $ Z_{i} $ and do not revert to the same size as $ P_i $ for each iteration. 

## SAT Encoding

### Boolean Variables
For each element $ x \in U $ :
- $ x_{P_i} $ : Indicates whether $ x $  is in $ P_i $ .
- $ x_{R_i} $ : Indicates whether $ x $  is in $ R_i $ .
- $ x_A_{i,j} $: Indicates whether $ x $ is in a se $ A_i,j $ where $ j $ indeces all possible sets generated by the operations from $ P_i $.


### Clauses for Initial Conditions
1. Every element is either in $ P_0 $  or $ R_0 $ :
   $$ (x_P \lor x_R) \quad \text{for each } x \in U $$
2. No element is in both $ P_0 $  and $ R_0 $ :
   $$ \neg (x_P \land x_R) \quad \text{for each } x \in U $$

### Clauses for Operations to Generate sets $ A_{i+1} $

#### Add Operation
For adding combinations of up to $ r $  elements from $ R_i $  to $ P_i $ :
- **Add one element $ y $  from $ R_i $  to $ P_i $**: 
   $$ \neg y_R_i \lor y_{A_{i+1,j}} \quad \text{for each } y \in R_i $$
   This ensures that if $ y $  is not in $ R_i $  (i.e., $ y_R_i $  is false), then $ y $  must be in $ A_{i+1,j} $ .

- **Generalize for adding combinations of up to $ r $  elements**:
   For every subset $ S \subseteq R_i $  where $ |S| \leq r $ :
   $$ \bigvee_{y \in S} y_{A_{i+1,j}} $$
   This ensures that at least one element in $ S $  is in $ A_{i+1,j} $ .

#### Remove Operation
For removing combinations of up to $ r $  elements from $ P_i $  to $ R_i $ :
- **Remove one element $ x $  from $ P_i $  to $ R_i $**:
   $$ x_P_i \lor \neg x_{A_{i+1,j}} \quad \text{for each } x \in P_i $$
   This ensures that if $ x $  is in $ P_i $  (i.e., $ x_P_i $  is true), then $ x $  must not be in $ A_{i+1,j} $ .

- **Generalize for removing combinations of up to $ r $  elements**:
   For every subset $ S \subseteq P_i $  where $ |S| \leq r $ :
   $$ \bigvee_{x \in S} \neg x_{A_{i+1,j}} $$
   This ensures that at least one element in $ S $  is not in $ A_{i+1,j} $ .

#### Swap Operation
For swapping combinations of up to $ r $  elements between $ P_0 $  and $ R_0 $ :
- **Swap one element $ y $  from $ R_i $  with $ x $  from $ P_i $**:
   $$ (\neg y_R_i \lor \neg x_P_i \lor (y_{A_{i+1,j}} \land \neg x_{A_{i+1,j}})) \quad \text{for each } y \in R_i, x \in P_i $$
   This ensures that if $ y $  is in $ R_i $  and $ x $  is in $ P_i $ , then $ y $  must be in $ A_{i+1,j} $  and $ x $  must not be in $ A_{i+1,j} $ .

- **Generalize for swapping combinations of up to $ r $  elements**:
   For every subset $ S_1 \subseteq P_i $  and $ S_2 \subseteq R_i $  where $ |S_1| = |S_2| \leq r $ :
   $$ \bigwedge_{y \in S_2, x \in S_1} (\neg y_R_i \lor \neg x_P_i \lor (y_{A_{i+1,j}} \land \neg x_{A_{i+1,j}})) $$
   This ensures that for every element in the subsets $ S_1 $  and $ S_2 $ , the swap condition holds.

### Clauses for Ensuring the Conditions
- **Ensuring $ Z_{i+1} $  is kept in $ P_{i+1} $**:
   If $ Z_{i+1} = (P_i \setminus P_{i+1}) \cup (P_i+1 \setminus P_i) $ :
   $$ \bigwedge_{z \in Z_{i+1}} z_{P_{i+1}} $$
   This ensures that elements in $ Z_{i+1} $  are in $ P_{i+1} $ .

- **Ensuring the size constraint**:
   This requires counting the number of true variables in $ P_{i+1} $  and ensuring it does    not equal the number of true variables in $ P_i $ . 

- **Ensuring Disjoint sets $ A_1, A_2, ..., A_i $**
    Finally, check that the sets $ A_1, A_2, ... $ are disjoint be adding clauses that enforce disjointness. 