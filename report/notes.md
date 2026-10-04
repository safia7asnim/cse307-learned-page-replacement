# Report Notes (Final Verified)

## 1. Introduction / Problem Framing

Page replacement is a core memory management problem. This study compares classical policies (FIFO, LRU, Optimal) against a simple learned/adaptive policy using a Decision Tree. We examine how each policy responds to a deliberate workload shift (locality-heavy/sequential → random access) using independent training and evaluation traces.

## 2. Classical Page Replacement Algorithms

- **FIFO**: Simple queue; evicts oldest-in.
- **LRU**: Approximates OPT by using past recency; effective under temporal locality.
- **Optimal (Belady)**: Theoretical benchmark—uses future knowledge to minimize faults.

## 3. Learned / Adaptive Policy

- **Model**: DecisionTreeClassifier (sklearn), max_depth=3, random_state=42.
- **Features**: recency (steps since last access), frequency (total accesses), age (time in memory). All past/current-available only.
- **Labeling**: Heuristic labels generated during simulation to identify good eviction candidates.
- **Training**: Trained on a separate independent synthetic training trace (training_seed=42). Training data is NOT taken from the evaluation trace (no data leakage).
- **Eviction**: Score resident pages in deterministic order; evict highest-scoring candidate; deterministic tie-breaking.
- **Runtime**: Decisions use only past/current information.

## 4. Experimental Setup

- **Environment**: Python 3, numpy, pandas, matplotlib, scikit-learn.
- **Training**: Independent synthetic training trace (length 2000, shift at 1000, training_seed=42).
- **Evaluation**: Independent synthetic evaluation trace (length 2000, shift at 1000, evaluation_seed=123). Same evaluation trace used for FIFO, LRU, Optimal, and Learned Policy.
- **Config**: frames=4, page_range=20, training_seed=42, evaluation_seed=123, evaluation_refs=2000, shift_point=1000.
- **Metrics**: hits, faults, hit_ratio, fault_ratio for before_shift, after_shift, overall.

## 5. Workload Shift

- **Training**: locality-heavy/sequential first half, random access second half (independent).
- **Evaluation**: locality-heavy/sequential first half (0–999), random access second half (1000–1999); shift at x=1000. Transition is explicit and visually shown in workload_trace.png.

## 6. Final Verified Results

Policy      Phase        Hits   Faults   Hit Ratio   Fault Ratio
----------- ----------- ------ -------- ----------- ------------
FIFO        before_shift   834      166       0.834        0.166
FIFO        after_shift    196      804       0.196        0.804
FIFO        overall       1030      970       0.515        0.485
LRU         before_shift   833      167       0.833        0.167
LRU         after_shift    196      804       0.196        0.804
LRU         overall       1029      971       0.5145       0.4855
Optimal     before_shift   878      122       0.878        0.122
Optimal     after_shift    442      558       0.442        0.558
Optimal     overall       1320      680       0.660        0.340
Learned     before_shift   833      167       0.833        0.167
Learned     after_shift    196      804       0.196        0.804
Learned     overall       1029      971       0.5145       0.4855

## 7. Discussion

- **Before shift (locality-heavy/sequential)**: LRU performs well (167 faults), close to Optimal (122). FIFO (166). Learned (167) similar under these conditions.
- **After shift (random access)**: Reduced locality causes sharp fault increase. Optimal still best (558); FIFO/LRU/Learned at 804.
- **Overall**: Optimal lowest (680). FIFO/LRU/Learned cluster (970–971). Same evaluation trace ensures fair comparison.
- **Locality effect**: LRU exploits temporal locality; random access breaks this.
- **Recency/frequency under randomness**: Past recency/frequency correlates less with future accesses under random pattern.

## 8. Conclusion

Classical policies behave as expected. Optimal is the valid theoretical benchmark. The learned policy is a simple, explainable, demonstrative component trained on a separate independent trace; results reflect the chosen features and labeling.

## 9. Limitations

- Synthetic workload for reproducibility/classroom demo.
- Small frame count (4); minimal feature set; DT depth limited.
- Learned policy not optimized; may not generalize beyond similar patterns.
- Optimal requires future knowledge (theoretical only).
