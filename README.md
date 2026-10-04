# CSE-307 Term Paper
## Learning-Augmented OS Heuristics: Classical Algorithms Meet Adaptive Prediction

### 1. Project Overview

This project implements classical page replacement algorithms (FIFO, LRU, Belady's Optimal) and a lightweight learned/adaptive page replacement policy using a DecisionTreeClassifier. The experiment evaluates all policies on the same independent evaluation trace containing a deliberate workload shift, with the learned model trained on a separate independent training trace.

### 2. Research Question

"How do classical and learned page replacement policies respond when the memory access pattern changes from locality-heavy/sequential to random behaviour?"

### 3. Algorithms

- **FIFO (First-In-First-Out)**: Replaces the page that entered memory earliest.
- **LRU (Least Recently Used)**: Replaces the page that has not been used for the longest time (true LRU).
- **Optimal (Belady's Algorithm)**: Looks into the future to replace the page whose next use is farthest in the future. This is a theoretical benchmark (not implementable in a real OS).
- **Learned (Decision Tree)**: Lightweight model trained separately on an independent training trace. Uses past-only features at runtime.

### 4. Learned Component

- **Model**: `sklearn.tree.DecisionTreeClassifier` (max_depth=3, random_state=42) — simple and explainable.
- **Features** (past-only, no future information): recency (steps since last access), frequency (total access count observed), age (steps since page entered memory).
- **Labeling**: Heuristic-based labeling during simulation to identify good eviction candidates. Optimal/Belady is not used at runtime.
- **Training**: Trained on an **independent synthetic training trace** (different seed from evaluation). Training data is not taken from the evaluation trace (no data leakage).
- **Eviction**: On page fault with full frames, compute features for each resident page and evict the candidate with highest predicted eviction score; deterministic tie-breaking.
- **Note**: The learned model is demonstrative and does not need to outperform Optimal; real results are reported as measured.

### 5. Workload Shift

- **Training trace**: Independent synthetic trace (locality-heavy/sequential then random) generated with its own fixed seed; used only for training.
- **Evaluation trace**: Independent synthetic trace generated with a different fixed seed. First half (references 0–999) is locality-heavy/sequential; second half (1000–1999) is random access. Clear shift at x=1000. The same evaluation trace is used for FIFO, LRU, Optimal, and Learned Policy.

### 6. Experiment Setup

- **Separation**: Training and evaluation are independent (different seeds).
- **Fair comparison**: All algorithms evaluated on identical evaluation trace.
- **Configurable**: frame count, training trace length, evaluation trace length, shift position, page range, training seed, evaluation seed.
- **Metrics**: page hits, page faults, hit ratio, fault ratio.
- **Phases**: before_shift, after_shift, overall.

### 7. Installation

```bash
pip install -r requirements.txt
```

### 8. How to Run

```bash
python main.py
```

### 9. Results

- CSV: `results/results.csv`
- Comparison plot: `results/comparison.png` (before/after fault counts)
- Workload visualization: `results/workload_trace.png` (entire evaluation trace, shift at x=1000)

See `report/notes.md` for measured numbers from the latest run.

### 10. Repository Structure

```
cse307-learned-page-replacement/
├── README.md
├── requirements.txt
├── main.py
├── src/
│   ├── __init__.py
│   ├── workload.py
│   ├── fifo.py
│   ├── lru.py
│   ├── optimal.py
│   ├── learned_policy.py
│   └── metrics.py
├── experiments/
│   ├── __init__.py
│   └── run_experiment.py
├── results/
│   ├── results.csv
│   ├── comparison.png
│   └── workload_trace.png
└── report/
    └── notes.md
```

### 11. Interpretation

Locality benefits recency-based policies (LRU) in the first phase. After shift to random access, temporal locality decreases and fault rates increase across all policies. Optimal remains the theoretical lower bound for the given trace. The lightweight learned policy is demonstrative; its performance reflects the chosen features, labeling, and training regime.



