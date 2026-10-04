# Learning-Augmented Page Replacement Under Workload Shift

**CSE-307 — Operating Systems | Term Paper, Part B | Track 1: Learned Page Replacement**

**Student ID:** 202414032

A comparison of classical and learned page-replacement policies when the memory-access pattern changes halfway through a run, from locality-heavy access to random access.

---

## 1. Overview

When a process references a page that is not in memory, a page fault occurs. If all frames are full, the operating system must choose a victim page to evict. Different policies choose differently, and how well they do depends on the reference pattern. Real workloads change over time.

This project implements three classical policies and one lightweight learned policy. It runs all of them on one synthetic trace whose access pattern changes at reference 1000.

| Policy | Idea |
|---|---|
| **FIFO** | Evicts the page that entered memory earliest. |
| **LRU** | Evicts the page not referenced for the longest time (relies on temporal locality). |
| **Optimal (Belady)** | Evicts the page whose next use is farthest in the future. It needs future knowledge, so it is only a theoretical benchmark. |
| **Learned** | A `DecisionTreeClassifier` scores the resident pages from past-only features and evicts the highest-scoring one. |

## 2. Research Question

> How do classical and learned page-replacement policies respond when the memory-access pattern changes from locality-heavy behavior to random access?

## 3. Learned Policy

- **Model:** `sklearn.tree.DecisionTreeClassifier` (`max_depth=3`, `random_state=42`). It is small and interpretable.
- **Features (past-only):**
  - *recency*: time steps since the page was last accessed
  - *frequency*: number of accesses observed
  - *age*: time steps since the page entered memory
- **Training labels:** produced by a simple hand-designed heuristic during a simulation of the training trace. A resident page is labelled a good eviction candidate if its recency is above 10 or its frequency is below 2. **The labels are not derived from Optimal/Belady decisions.**
- **Training data:** a separate synthetic trace, independent of the evaluation trace.
- **At run time:** when a page fault occurs with all frames full, features are computed for each resident page and the tree gives each page an eviction score. The highest-scoring page is evicted. Ties are broken deterministically, preferring larger recency and then the smaller page number. No future information is used.
- **Not** deep learning and **not** reinforcement learning. It is a lightweight learned heuristic.

## 4. Experimental Setup

| Setting | Value |
|---|---|
| Memory frames | 4 |
| Distinct pages (page range) | 20 |
| Training trace length | 2000 references |
| Evaluation trace length | 2000 references |
| Training seed | 42 |
| Evaluation seed | 123 |
| Workload shift position | reference 1000 |
| Evaluation, references 0–999 | locality-heavy access |
| Evaluation, references 1000–1999 | random access |

- The **same evaluation trace** is used for FIFO, LRU, Optimal, and the Learned policy, so the comparison is fair.
- The training trace is generated separately, with a different seed, and is used only to train the decision tree.
- **Metrics:** page hits, page faults, hit ratio, and fault ratio, for the part before the shift, the part after the shift, and the whole trace.
- `main.py` runs consistency checks at the end: hits + faults equals the number of references in each phase, phase totals add up to the overall totals, and ratios lie in [0, 1]. Optimal must also have no more faults than FIFO or LRU. It prints `Validation checks: PASSED` if all of them hold.

## 5. Results

Page faults on the evaluation trace (4 frames, 2000 references, shift at reference 1000):

| Policy | Before Shift Faults | After Shift Faults | Overall Faults | Overall Hit Ratio |
|---|---:|---:|---:|---:|
| FIFO | 166 | 804 | 970 | 0.515 |
| LRU | 167 | 804 | 971 | 0.5145 |
| Optimal | 122 | 558 | 680 | 0.660 |
| Learned | 167 | 804 | 971 | 0.5145 |

The per-phase hits, faults, hit ratios, and fault ratios for every policy are in [`results/results.csv`](results/results.csv).

**Figures**

- `results/comparison.png`: page-fault counts before and after the shift, per policy.
- `results/workload_trace.png`: the evaluation trace, with the shift marked at reference 1000.

### Summary of findings

- Every policy has far more page faults after the workload becomes random.
- Before the shift, locality lets history-based policies work reasonably well. FIFO, LRU, and Learned all have 166–167 faults, against 122 for Optimal.
- After the shift, recent history says little about future references. FIFO, LRU, and Learned all have 804 faults.
- **The learned policy performs about the same as LRU in this experiment; it does not outperform it.** A lightweight learned policy built on past-access features is also sensitive to the workload shift.
- Optimal does much better because it knows the future. It is a theoretical benchmark, not a practical online policy.

## 6. Limitations

- The workload is synthetic; no real application memory trace is used.
- Only 4 memory frames and two broad workload patterns (locality-heavy, then random) are tested.
- Only one lightweight decision tree is evaluated, using a small hand-designed feature set.
- Training labels come from a simple heuristic, not from an optimal policy.
- Optimal needs future information, so it cannot be built as a practical online policy.

## 7. Installation

Requires Python 3 and the packages in `requirements.txt` (`numpy`, `pandas`, `matplotlib`, `scikit-learn`).

```bash
# optional: create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## 8. How to Run

From the project root:

```bash
python main.py
```

This will:

1. Generate the training and evaluation traces.
2. Run FIFO, LRU, and Optimal on the evaluation trace.
3. Train the decision tree on the training trace and run the Learned policy on the evaluation trace.
4. Print the results table and run the validation checks.
5. Save `results/results.csv`, `results/comparison.png`, and `results/workload_trace.png`.

Settings such as frame count, trace lengths, seeds, shift position, and page range are defined in the `config` dictionary in `main.py`.

## 9. Repository Structure

```
.
├── README.md
├── requirements.txt
├── main.py                      # entry point: config, run, validation, plots, CSV
├── src/
│   ├── workload.py              # synthetic trace generator with a workload shift
│   ├── fifo.py                  # FIFO page replacement
│   ├── lru.py                   # LRU page replacement
│   ├── optimal.py               # Optimal (Belady) page replacement
│   ├── learned_policy.py        # DecisionTreeClassifier-based policy
│   └── metrics.py               # small helper for hit/fault ratios
├── experiments/
│   └── run_experiment.py        # runs all policies and computes per-phase metrics
├── results/
│   ├── results.csv
│   ├── comparison.png
│   └── workload_trace.png
└── report/
    ├── notes.md                 # working notes with the verified results
    ├── term_paper.tex           # LaTeX source of the written report
    └── references.bib           # bibliography
```


## 10. References

1. A. Silberschatz, P. B. Galvin, and G. Gagne, *Operating System Concepts*, 10th ed. Wiley, 2018.
2. A. S. Tanenbaum and H. Bos, *Modern Operating Systems*, 4th ed. Pearson, 2015.
3. L. A. Belady, "A study of replacement algorithms for a virtual-storage computer," *IBM Systems Journal*, vol. 5, no. 2, pp. 78–101, 1966.
4. F. Pedregosa et al., "Scikit-learn: Machine Learning in Python," *Journal of Machine Learning Research*, vol. 12, pp. 2825–2830, 2011.
5. T. Hastie, R. Tibshirani, and J. Friedman, *The Elements of Statistical Learning*, 2nd ed. Springer, 2009.
