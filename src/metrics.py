def compute_metrics(page_hits, page_faults, total_refs):
    hit_ratio = page_hits / total_refs if total_refs > 0 else 0.0
    fault_ratio = page_faults / total_refs if total_refs > 0 else 0.0
    return {
        'page_hits': page_hits,
        'page_faults': page_faults,
        'hit_ratio': hit_ratio,
        'fault_ratio': fault_ratio,
        'total_refs': total_refs
    }
