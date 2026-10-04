from collections import defaultdict, deque
import numpy as np


class SimpleLearnedPolicy:
    """
    Simple learned page replacement policy using DecisionTreeClassifier.
    Features (explainable, past-only):
    - recency: number of accesses since last use (larger = less recently used)
    - frequency: access count
    - age: steps since page entered memory (approx)
    Labels: target eviction preference (1 = good eviction candidate)
    """

    def __init__(self):
        self.model = None
        self.last_access = {}
        self.access_count_total = defaultdict(int)
        self.recent_accesses = deque(maxlen=100)
        self.page_entry_time = {}
        self.global_time = 0
        self.trained = False

    def _extract_features(self, page, current_time):
        recency = (current_time - self.last_access.get(page, current_time - 1000))
        frequency = self.access_count_total.get(page, 0)
        age = (current_time - self.page_entry_time.get(page, current_time))
        return [recency, frequency, age]

    def simulate_and_label(self, page_refs, num_frames, oracle='simple'):
        X, y = [], []
        frames = set()
        last_access = {}
        access_count = defaultdict(int)
        entry_time = {}
        t = 0
        for ref in page_refs:
            access_count[ref] += 1
            last_access[ref] = t
            if ref not in frames:
                if len(frames) < num_frames:
                    frames.add(ref)
                    entry_time[ref] = t
                else:
                    candidates = sorted(list(frames))
                    for c in candidates:
                        rec = t - last_access.get(c, t)
                        freq = access_count.get(c, 0)
                        age = t - entry_time.get(c, t)
                        X.append([rec, freq, age])
                        if oracle == 'simple':
                            label = 1 if (rec > 10 or freq < 2) else 0
                        else:
                            label = 1 if rec >= 5 else 0
                        y.append(label)
                    victim = candidates[0] if candidates else ref
                    frames.discard(victim)
                    frames.add(ref)
                    entry_time[ref] = t
            t += 1
        return np.array(X) if X else np.array([]), np.array(y) if y else np.array([])

    def train(self, page_refs, num_frames):
        try:
            from sklearn.tree import DecisionTreeClassifier
        except Exception:
            self.trained = False
            return
        X, y = self.simulate_and_label(page_refs, num_frames, oracle='simple')
        if len(X) == 0 or len(y) == 0:
            self.model = DecisionTreeClassifier(max_depth=3, random_state=42)
            self.trained = True
            return
        self.model = DecisionTreeClassifier(max_depth=3, random_state=42)
        self.model.fit(X, y)
        self.trained = True

    def predict_eviction_scores(self, pages, current_time):
        if not self.trained or self.model is None:
            scores = []
            for p in pages:
                rec = current_time - self.last_access.get(p, current_time - 1000)
                scores.append(rec)
            return scores
        feats = []
        for p in pages:
            feats.append(self._extract_features(p, current_time))
        try:
            proba = self.model.predict_proba(feats)
            scores = [row[1] if row.shape[0] > 1 else 0.0 for row in proba]
        except Exception:
            scores = [current_time - self.last_access.get(p, current_time - 1000) for p in pages]
        return scores

    def replace(self, page_refs, num_frames):
        if num_frames <= 0:
            total = len(page_refs)
            return {'page_faults': total, 'page_hits': 0, 'hit_ratio': 0.0, 'fault_ratio': 1.0, 'faults_list': [True]*total}
        frames = []
        self.last_access.clear()
        self.access_count_total.clear()
        self.page_entry_time.clear()
        self.global_time = 0
        page_faults = 0
        page_hits = 0
        faults_list = []
        for ref in page_refs:
            self.access_count_total[ref] += 1
            if ref in frames:
                page_hits += 1
                faults_list.append(False)
                self.last_access[ref] = self.global_time
            else:
                page_faults += 1
                faults_list.append(True)
                if len(frames) < num_frames:
                    frames.append(ref)
                    self.page_entry_time[ref] = self.global_time
                    self.last_access[ref] = self.global_time
                else:
                    # evaluate candidates in deterministic order
                    candidates = sorted(frames)
                    # build map back to original positions if needed by not necessary; we will pop from frames list
                    # get scores for candidates in that order
                    scores = self.predict_eviction_scores(candidates, self.global_time)
                    best_idx_in_cand = 0
                    for i in range(1, len(scores)):
                        if scores[i] > scores[best_idx_in_cand]:
                            best_idx_in_cand = i
                        elif scores[i] == scores[best_idx_in_cand]:
                            # deterministic tie-break: prefer larger recency, then smaller page number
                            c_cur = candidates[i]
                            c_best = candidates[best_idx_in_cand]
                            rec_cur = self.global_time - self.last_access.get(c_cur, self.global_time - 10**9)
                            rec_best = self.global_time - self.last_access.get(c_best, self.global_time - 10**9)
                            if rec_cur != rec_best:
                                if rec_cur > rec_best:
                                    best_idx_in_cand = i
                            else:
                                if c_cur < c_best:
                                    best_idx_in_cand = i
                    victim = candidates[best_idx_in_cand]
                    # remove victim from frames (first match)
                    try:
                        vpos = frames.index(victim)
                        frames.pop(vpos)
                    except ValueError:
                        # fallback: remove by scanning
                        for j in range(len(frames) - 1, -1, -1):
                            if frames[j] == victim:
                                frames.pop(j)
                                break
                    frames.append(ref)
                    self.page_entry_time[ref] = self.global_time
                    self.last_access[ref] = self.global_time
            self.global_time += 1
        hit_ratio = page_hits / len(page_refs) if page_refs else 0.0
        fault_ratio = page_faults / len(page_refs) if page_refs else 0.0
        return {
            'page_faults': page_faults,
            'page_hits': page_hits,
            'hit_ratio': hit_ratio,
            'fault_ratio': fault_ratio,
            'faults_list': faults_list
        }
