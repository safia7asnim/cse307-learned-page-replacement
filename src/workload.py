import random


def generate_workload(total_refs=2000, page_range=20, shift_point=1000, seed=42, locality_window=5):
    """
    Generate synthetic page access trace with deliberate workload shift.
    First half (0..shift_point-1): locality-heavy/sequential
    Second half (shift_point..end): random access
    """
    rng = random.Random(seed)
    trace = []
    # Before shift: locality-heavy/sequential
    for i in range(shift_point):
        if i < locality_window:
            trace.append(rng.randint(0, min(4, page_range - 1)))
        else:
            if rng.random() < 0.8:
                trace.append(trace[i - rng.randint(1, 3)])
            else:
                trace.append(rng.randint(0, page_range - 1))
    # After shift: random access
    for i in range(total_refs - shift_point):
        trace.append(rng.randint(0, page_range - 1))
    return trace
