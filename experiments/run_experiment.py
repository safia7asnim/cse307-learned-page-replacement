from src.workload import generate_workload
from src.fifo import fifo_page_replacement
from src.lru import lru_page_replacement
from src.optimal import optimal_page_replacement
from src.learned_policy import SimpleLearnedPolicy


def phase_metrics(result, faults_list, shift_point):
    total = len(faults_list)
    before_count = min(shift_point, total)
    after_count = total - before_count
    before_faults = sum(1 for i in range(before_count) if faults_list[i])
    after_faults = sum(1 for i in range(before_count, total) if faults_list[i])
    before_hits = before_count - before_faults
    after_hits = after_count - after_faults
    return {
        'before': {
            'page_hits': before_hits,
            'page_faults': before_faults,
            'hit_ratio': before_hits / before_count if before_count > 0 else 0.0,
            'fault_ratio': before_faults / before_count if before_count > 0 else 0.0
        },
        'after': {
            'page_hits': after_hits,
            'page_faults': after_faults,
            'hit_ratio': after_hits / after_count if after_count > 0 else 0.0,
            'fault_ratio': after_faults / after_count if after_count > 0 else 0.0
        },
        'overall': {
            'page_hits': result['page_hits'],
            'page_faults': result['page_faults'],
            'hit_ratio': result['hit_ratio'],
            'fault_ratio': result['fault_ratio']
        }
    }


def run_experiment(config):
    training_trace = generate_workload(
        total_refs=config['training_trace_length'],
        page_range=config['page_range'],
        shift_point=config['training_shift_point'],
        seed=config['training_seed']
    )
    eval_trace = generate_workload(
        total_refs=config['evaluation_trace_length'],
        page_range=config['page_range'],
        shift_point=config['shift_point'],
        seed=config['evaluation_seed']
    )

    frames = config['frame_count']
    shift = config['shift_point']
    results_rows = []

    print("Running FIFO...")
    fifo_res = fifo_page_replacement(eval_trace, frames)
    p = phase_metrics(fifo_res, fifo_res['faults_list'], shift)
    for phase_name, vals in [('before_shift', p['before']), ('after_shift', p['after']), ('overall', p['overall'])]:
        results_rows.append(['FIFO', phase_name, vals['page_hits'], vals['page_faults'], vals['hit_ratio'], vals['fault_ratio']])

    print("Running LRU...")
    lru_res = lru_page_replacement(eval_trace, frames)
    p = phase_metrics(lru_res, lru_res['faults_list'], shift)
    for phase_name, vals in [('before_shift', p['before']), ('after_shift', p['after']), ('overall', p['overall'])]:
        results_rows.append(['LRU', phase_name, vals['page_hits'], vals['page_faults'], vals['hit_ratio'], vals['fault_ratio']])

    print("Running Optimal...")
    opt_res = optimal_page_replacement(eval_trace, frames)
    p = phase_metrics(opt_res, opt_res['faults_list'], shift)
    for phase_name, vals in [('before_shift', p['before']), ('after_shift', p['after']), ('overall', p['overall'])]:
        results_rows.append(['Optimal', phase_name, vals['page_hits'], vals['page_faults'], vals['hit_ratio'], vals['fault_ratio']])

    print("\nTraining learned policy...")
    lp = SimpleLearnedPolicy()
    lp.train(training_trace, frames)
    print("Training complete.")
    print("Running Learned Policy...")
    lp_res = lp.replace(eval_trace, frames)
    p = phase_metrics(lp_res, lp_res['faults_list'], shift)
    for phase_name, vals in [('before_shift', p['before']), ('after_shift', p['after']), ('overall', p['overall'])]:
        results_rows.append(['Learned', phase_name, vals['page_hits'], vals['page_faults'], vals['hit_ratio'], vals['fault_ratio']])

    return training_trace, eval_trace, results_rows
