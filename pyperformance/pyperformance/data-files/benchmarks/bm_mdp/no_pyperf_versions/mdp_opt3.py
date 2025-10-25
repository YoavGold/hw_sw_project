import collections
from functools import lru_cache


def topoSort(roots, getParents):
    results = []
    visited = set()
    stack = [(node, 0) for node in roots]
    while stack:
        current, state = stack.pop()
        if state == 0:
            if current not in visited:
                visited.add(current)
                stack.append((current, 1))
                stack.extend((parent, 0) for parent in getParents(current))
        else:
            assert(current in visited)
            results.append(current)
    return results

@lru_cache(maxsize=None)
def getDamages(L, A, D, B, stab, te):
    x = (2 * L) // 5
    x = ((x + 2) * A * B) // (D * 50) + 2
    if stab:
        x += x // 2
    x = int(x * te)
    return [(x * z) // 255 for z in range(217, 256)]

@lru_cache(maxsize=None)
def getCritDist(L, p, A1, A2, D1, D2, B, stab, te):
    p = min(p, 1.0)
    norm = getDamages(L, A1, D1, B, stab, te)
    crit = getDamages(L * 2, A2, D2, B, stab, te)
    dist = {}
    mult_norm = (1.0 - p) / len(norm)
    mult_crit = p / len(crit)
    for x in norm:
        dist[x] = dist.get(x, 0.0) + mult_norm
    for x in crit:
        dist[x] = dist.get(x, 0.0) + mult_crit
    return dist

def plus12(x):
    return x + x // 8

stats_t = collections.namedtuple('stats_t', ['atk', 'df', 'speed', 'spec'])
NOMODS = stats_t(0, 0, 0, 0)


fixeddata_t = collections.namedtuple(
    'fixeddata_t', ['maxhp', 'stats', 'lvl', 'badges', 'basespeed'])
halfstate_t = collections.namedtuple(
    'halfstate_t', ['fixed', 'hp', 'status', 'statmods', 'stats'])


def applyHPChange(hstate, change):
    hp = min(hstate.fixed.maxhp, max(0, hstate.hp + change))
    return hstate._replace(hp=hp)


def applyBadgeBoosts(badges, stats):
    return stats_t(*[(plus12(x) if b else x) for x, b in zip(stats, badges)])


attack_stats_t = collections.namedtuple(
    'attack_stats_t', ['power', 'isspec', 'stab', 'te', 'crit'])
attack_data = {
    'Ember': attack_stats_t(40, True, True, 0.5, False),
    'Dig': attack_stats_t(100, False, False, 1.0, False),
    'Slash': attack_stats_t(70, False, False, 1.0, True),
    'Water Gun': attack_stats_t(40, True, True, 2.0, False),
    'Bubblebeam': attack_stats_t(65, True, True, 2.0, False),
}


def _applyActionSide1(state, act):
    me, them, extra = state
    if act == 'Super Potion':
        me2 = applyHPChange(me, 50)
        return {(me2, them, extra): 1.0}

    m = attack_data[act]
    aind = 3 if m.isspec else 0
    dind = 3 if m.isspec else 1
    pdiv = 64 if m.crit else 512
    dmg_dist = getCritDist(me.fixed.lvl, float(me.fixed.basespeed)/pdiv,
                           me.stats[aind], me.fixed.stats[aind],
                           them.stats[dind], them.fixed.stats[dind],
                           m.power, m.stab, m.te)
    dist = {}
    for dmg, p in dmg_dist.items():
        them2 = applyHPChange(them, -dmg)
        key = (me, them2, extra)
        dist[key] = dist.get(key, 0.0) + p
    return dist

def _applyAction(state, side, act):
    if side == 0:
        return _applyActionSide1(state, act)
    else:
        me, them, extra = state
        dist = _applyActionSide1((them, me, extra), act)
        return {(k[1], k[0], k[2]): v for k, v in dist.items()}


class Battle(object):
    def __init__(self):
        self.successors = {}
        self.min = collections.defaultdict(float)
        self.max = collections.defaultdict(lambda: 1.0)
        self.frozen = set()
        self.win  = (4, True)
        self.loss = (4, False)
        self.max[self.loss] = 0.0
        self.min[self.win]  = 1.0
        self.frozen.update([self.win, self.loss])

    def _getSuccessorsA(self, statep):
        # return a concrete list
        _, state = statep
        return [(1, state, 'Dig'), (1, state, 'Super Potion')]

    def _applyActionPair(self, state, side1, act1, side2, act2, dist, pmult):
        for newstate, p in _applyAction(state, side1, act1).items():
            if newstate[0].hp == 0:
                newstatep = self.loss
            elif newstate[1].hp == 0:
                newstatep = self.win
            else:
                newstatep = (2, newstate, side2, act2)
            dist[newstatep] = dist.get(newstatep, 0.0) + p * pmult

    def _getSuccessorsB(self, statep):
        _, state, action = statep
        dist = {}
        # enemy move probabilities
        for eact, p in (('Water Gun', 64.0/130.0), ('Bubblebeam', 66.0/130.0)):
            priority1 = state[0].stats.speed + (10000 if action == 'Super Potion' else 0)
            priority2 = state[1].stats.speed
            if   priority1 > priority2:
                self._applyActionPair(state, 0, action, 1, eact, dist, p)
            elif priority1 < priority2:
                self._applyActionPair(state, 1, eact, 0, action, dist, p)
            else:
                self._applyActionPair(state, 0, action, 1, eact, dist, p * 0.5)
                self._applyActionPair(state, 1, eact, 0, action, dist, p * 0.5)

        pairs = sorted(dist.items(), key=lambda t: (-t[1], t[0]))
        return pairs

    def _getSuccessorsC(self, statep):
        _, state, side, action = statep
        dist = {}
        for newstate, p in _applyAction(state, side, action).items():
            if newstate[0].hp == 0:
                newstatep = self.loss
            elif newstate[1].hp == 0:
                newstatep = self.win
            else:
                newstatep = (0, newstate)
            dist[newstatep] = dist.get(newstatep, 0.0) + p
        pairs = sorted(dist.items(), key=lambda t: (-t[1], t[0]))
        return pairs

    def getSuccessors(self, statep):
        cached = self.successors.get(statep)
        if cached is not None:
            return cached[0]  # pairs_or_states view

        st = statep[0]
        if st == 0:
            states = self._getSuccessorsA(statep)   # list of states
            states_only = states
            pairs_or_states = states
        else:
            if st == 1:
                pairs = self._getSuccessorsB(statep)   # list of (state, p), sorted
            else:
                pairs = self._getSuccessorsC(statep)
            pairs_or_states = pairs
            states_only = [sp for (sp, _) in pairs]

        self.successors[statep] = (pairs_or_states, states_only)
        return pairs_or_states

    def getSuccessorsList(self, statep):
        if statep[0] == 4:
            return []
        cached = self.successors.get(statep)
        if cached is not None:
            return cached[1]  # states_only
        # if not cached yet, compute once
        self.getSuccessors(statep)
        return self.successors[statep][1]

    # build graph once, assign integer IDs
    def build_graph(self, initial_statep):
        from collections import deque
        q = deque([initial_statep])
        id_of = {initial_statep: 0}
        states = [initial_statep]
        kinds = []          # 0,1,2,4 per state id
        succ_states = []    # for st==0: list[id]
        succ_pairs  = []    # for st in {1,2}: list[(id, prob)]

        while q:
            sp = q.popleft()
            i = id_of[sp]
            st = sp[0]

            if st == 0:
                nxt = self.getSuccessors(sp)   # list[statep]
                ids = []
                for sp2 in nxt:
                    if sp2 not in id_of:
                        id_of[sp2] = len(states); states.append(sp2); q.append(sp2)
                    ids.append(id_of[sp2])
                kinds.append(0)
                succ_states.append(ids)
                succ_pairs.append(None)

            elif st == 4:
                kinds.append(4)
                succ_states.append([])
                succ_pairs.append([])

            else:
                nxt = self.getSuccessors(sp)   # list[(statep, p)], already sorted
                pairs = []
                for sp2, p in nxt:
                    if sp2 not in id_of:
                        id_of[sp2] = len(states); states.append(sp2); q.append(sp2)
                    pairs.append((id_of[sp2], p))
                kinds.append(st)
                succ_states.append(None)
                succ_pairs.append(pairs)

        return id_of, states, kinds, succ_states, succ_pairs

    def evaluate(self, tolerance=0.15):
        badges = (1, 0, 0, 0)
        starfixed = fixeddata_t(59, stats_t(40, 44, 56, 50), 11, NOMODS, 115)
        starhalf  = halfstate_t(starfixed, 59, 0, NOMODS, stats_t(40, 44, 56, 50))
        charfixed = fixeddata_t(63, stats_t(39, 34, 46, 38), 26, badges, 65)
        charhalf  = halfstate_t(charfixed, 63, 0, NOMODS, applyBadgeBoosts(badges, stats_t(39, 34, 46, 38)))
        initial_state  = (charhalf, starhalf, 0)
        initial_statep = (0, initial_state)

        # Build integer-ID graph once
        id_of, states, kinds, succ_states, succ_pairs = self.build_graph(initial_statep)
        n = len(states)

        # Arrays instead of dicts for hot loop
        dmin_arr = [0.0] * n
        dmax_arr = [1.0] * n
        frozen_a = [False] * n

        # seed terminals exactly as before
        if self.loss in id_of:
            i_loss = id_of[self.loss]
            dmax_arr[i_loss] = 0.0
            frozen_a[i_loss] = True
        if self.win in id_of:
            i_win = id_of[self.win]
            dmin_arr[i_win] = 1.0
            frozen_a[i_win] = True

        i_init = id_of[initial_statep]


        order_ids = [id_of[sp] for sp in topoSort([initial_statep], self.getSuccessorsList)]

        #  Value iteration with arrays
        while dmax_arr[i_init] - dmin_arr[i_init] > tolerance:
            for i in order_ids:
                if frozen_a[i]:
                    continue

                k = kinds[i]
                if k == 0:
                    # choice node
                    best_min = float('-inf')
                    best_max = float('-inf')
                    for j in succ_states[i]:
                        vmin = dmin_arr[j]; vmax = dmax_arr[j]
                        if vmin > best_min: best_min = vmin
                        if vmax > best_max: best_max = vmax
                    dmin_arr[i] = best_min
                    dmax_arr[i] = best_max

                elif k == 1 or k == 2:
                    # chance node
                    smin = 0.0
                    smax = 0.0
                    for j, p in succ_pairs[i]:
                        smin += dmin_arr[j] * p
                        smax += dmax_arr[j] * p
                    dmin_arr[i] = smin
                    dmax_arr[i] = smax

                if dmin_arr[i] >= dmax_arr[i]:
                    mid = 0.5 * (dmin_arr[i] + dmax_arr[i])
                    dmin_arr[i] = dmax_arr[i] = mid
                    frozen_a[i] = True

        return 0.5 * (dmax_arr[i_init] + dmin_arr[i_init])



def bench_mdp(loops):
    expected = 0.89873589887
    max_diff = 1e-6
    result = None
    for _ in range(loops):
        result = Battle().evaluate(0.192)
    if abs(result - expected) > max_diff:
        raise Exception("invalid result: got %s, expected %s "
                        "(diff: %s, max diff: %s)"
                        % (result, expected, result - expected, max_diff))
    return result

def main():
    loops = 10
    bench_mdp(loops)
    print(f"MDP benchmark completed with {loops} loops")

if __name__ == "__main__":
    main()
