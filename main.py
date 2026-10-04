import os
import csv
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from experiments.run_experiment import run_experiment


def main():
    config = {
        'frame_count': 4,
        'training_trace_length': 2000,
        'training_shift_point': 1000,
        'evaluation_trace_length': 2000,
        'shift_point': 1000,
        'page_range': 20,
        'training_seed': 42,
        'evaluation_seed': 123
    }
    print("CSE-307 Learned Page Replacement Experiment")
    print("=" * 44)
    print("\nConfiguration")
    print(f"Frames: {config['frame_count']}")
    print(f"Training trace length: {config['training_trace_length']}")
    print(f"Evaluation trace length: {config['evaluation_trace_length']}")
    print(f"Shift position: {config['shift_point']}")
    print(f"Page range: {config['page_range']}")
    print(f"Training seed: {config['training_seed']}")
    print(f"Evaluation seed: {config['evaluation_seed']}")

    print("\nGenerating training and evaluation traces...")
    training_trace, eval_trace, rows = run_experiment(config)

    os.makedirs('results', exist_ok=True)
    csv_path = os.path.join('results', 'results.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['policy', 'phase', 'page_hits', 'page_faults', 'hit_ratio', 'fault_ratio'])
        writer.writerows(rows)

    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except Exception:
        plt = None

    if plt is not None:
        policies = ['FIFO', 'LRU', 'Optimal', 'Learned']
        before = []
        after = []
        for p in policies:
            for r in rows:
                if r[0] == p and r[1] == 'before_shift':
                    before.append(r[3])
                if r[0] == p and r[1] == 'after_shift':
                    after.append(r[3])
        x = range(len(policies))
        width = 0.35
        plt.figure(figsize=(8, 5))
        plt.bar([i - width / 2 for i in x], before, width, label='Before Shift')
        plt.bar([i + width / 2 for i in x], after, width, label='After Shift')
        plt.xticks(x, policies)
        plt.ylabel('Page Fault Count')
        plt.title('Page Fault Comparison Before and After Workload Shift')
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join('results', 'comparison.png'))
        plt.close()

        plt.figure(figsize=(10, 4))
        plt.plot(eval_trace, marker='.', markersize=1, linestyle='-', alpha=0.5)
        plt.axvline(x=config['shift_point'], color='red', linestyle='--', label='Workload Shift')
        plt.xlabel('Reference Index (0 to 1999)')
        plt.ylabel('Page Number')
        plt.title('Evaluation Workload Trace (Entire Trace)')
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join('results', 'workload_trace.png'))
        plt.close()

    total_eval = config['evaluation_trace_length']
    shift = config['shift_point']
    before_refs = min(shift, total_eval)
    after_refs = total_eval - before_refs

    all_passed = True
    for policy, phase, hits, faults, hit_ratio, fault_ratio in rows:
        hits_i = int(hits)
        faults_i = int(faults)
        hr_f = float(hit_ratio)
        fr_f = float(fault_ratio)
        if phase == 'overall':
            if hits_i + faults_i != total_eval:
                all_passed = False
        elif phase == 'before_shift':
            if hits_i + faults_i != before_refs:
                all_passed = False
        elif phase == 'after_shift':
            if hits_i + faults_i != after_refs:
                all_passed = False
        if hr_f < 0.0 or hr_f > 1.0 or fr_f < 0.0 or fr_f > 1.0:
            all_passed = False

    by_p = {}
    for policy, phase, hits, faults, hit_ratio, fault_ratio in rows:
        by_p.setdefault(policy, {})
        by_p[policy][phase] = (int(hits), int(faults))

    for p in by_p:
        v = by_p[p]
        if 'overall' in v and 'before_shift' in v and 'after_shift' in v:
            o_h, o_f = v['overall']
            b_h, b_f = v['before_shift']
            a_h, a_f = v['after_shift']
            if o_h != b_h + a_h or o_f != b_f + a_f:
                all_passed = False

    if 'Optimal' in by_p and 'FIFO' in by_p and 'LRU' in by_p:
        if by_p['Optimal']['overall'][1] > by_p['FIFO']['overall'][1] or by_p['Optimal']['overall'][1] > by_p['LRU']['overall'][1]:
            all_passed = False

    print("\nRESULTS")
    print("Policy      Before Faults   After Faults   Overall Faults   Hit Ratio")
    for p in ['FIFO', 'LRU', 'Optimal', 'Learned']:
        b = a = o = hr = None
        for policy, phase, hits, faults, hit_ratio, fault_ratio in rows:
            if policy == p and phase == 'before_shift':
                b = faults
            if policy == p and phase == 'after_shift':
                a = faults
            if policy == p and phase == 'overall':
                o = faults
                hr = f"{float(hit_ratio):.3f}"
        print(f"{p:<11}{b:<15}{a:<15}{o:<17}{hr}")

    if not all_passed:
        raise SystemExit("Validation checks: FAILED")
    print("\nValidation checks: PASSED")
    print(f"\nResults saved:\nresults/results.csv\nresults/comparison.png\nresults/workload_trace.png")


if __name__ == '__main__':
    main()
