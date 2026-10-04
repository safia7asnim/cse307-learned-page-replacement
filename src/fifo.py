def fifo_page_replacement(page_refs, num_frames):
    if num_frames <= 0:
        total = len(page_refs)
        return {
            'page_faults': total,
            'page_hits': 0,
            'hit_ratio': 0.0,
            'fault_ratio': 1.0,
            'faults_list': [True] * total
        }
    frames = []
    page_faults = 0
    page_hits = 0
    faults_list = []
    for ref in page_refs:
        if ref in frames:
            page_hits += 1
            faults_list.append(False)
        else:
            page_faults += 1
            faults_list.append(True)
            if len(frames) < num_frames:
                frames.append(ref)
            else:
                frames.pop(0)
                frames.append(ref)
    hit_ratio = page_hits / len(page_refs) if page_refs else 0.0
    fault_ratio = page_faults / len(page_refs) if page_refs else 0.0
    return {
        'page_faults': page_faults,
        'page_hits': page_hits,
        'hit_ratio': hit_ratio,
        'fault_ratio': fault_ratio,
        'faults_list': faults_list
    }
