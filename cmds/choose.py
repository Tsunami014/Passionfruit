import math
import random
import numpy as np
from read import WrapPrinter, wait

from .edit import edit_file
import dir

def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))

LAMBDA = 0.5 # prior strength (pull of every score toward 0)
Y = [ # target probability that item shown as A beats item shown as B
    0.9, # A much
    0.7, # A slight
    0.3, # B slight
    0.1, # B much
]
STOP_PRIORITY = 0.1 # stop when the best remaining pair's misorder prob is below this
CAP_MULT = 2 # max questions = min(n(n-1)/2, CAP_MULT * n)
FLOOR_MULT = 1 # min questions = min(n(n-1)/2, FLOOR_MULT * n)
TIE_BAND = 0.01 # pairs within this of the best priority count as tied

TIER_THRESHOLD = 0.35  # item joins the tier leader's tier if misorder(leader, item) >= this
MAX_TIERS = 5
TIER_LABELS = ["S", "A", "B", "C", "D", "E", "F"]


def build(n, comparisons, theta):
    """Gradient g and Hessian H of the regularised log-likelihood at theta."""
    g = -LAMBDA * theta
    H = LAMBDA * np.eye(n)
    for (i, j, y) in comparisons:
        p = sigmoid(theta[i] - theta[j])
        g[i] += (y - p)
        g[j] -= (y - p)
        w = p * (1 - p)
        H[i, i] += w
        H[j, j] += w
        H[i, j] -= w
        H[j, i] -= w
    return g, H


def fit(n, comparisons, theta0=None):
    """Return (theta, Sigma). Sigma is the n x n covariance of the scores."""
    theta = np.zeros(n) if theta0 is None else np.array(theta0, dtype=float)
    for _ in range(6):
        g, H = build(n, comparisons, theta)
        step = np.linalg.solve(H, g)
        theta = theta + step
        if np.max(np.abs(step)) < 1e-4:
            break
    _, H = build(n, comparisons, theta)  # H at the final theta
    if n > 100:
        Sigma = np.diag(1.0 / np.diag(H)) # cheap approximation for large n
    else:
        Sigma = np.linalg.inv(H)
    return theta, Sigma


def misorder(theta, Sigma, i, j):
    """Probability that the pair's true order is opposite to the current one."""
    d = theta[i] - theta[j]
    v = Sigma[i, i] + Sigma[j, j] - 2 * Sigma[i, j]
    z = abs(d) / math.sqrt(v)
    return 0.5 * math.erfc(z / math.sqrt(2))  # Phi(-z)


def final_scores(theta):
    """0-100 scores, 50 = average. Not stretched; sort order equals theta order."""
    centered = theta - np.mean(theta)
    return [100 * sigmoid(t) for t in centered]

def make_tiers(theta, Sigma, threshold=TIER_THRESHOLD, max_tiers=MAX_TIERS):
    """Return a list of tiers (best first); each tier is a list of item indices."""
    order = [int(k) for k in np.argsort(-theta)]
    tiers = []
    leader = None
    for k in order:
        if leader is not None and misorder(theta, Sigma, leader, k) >= threshold:
            tiers[-1].append(k)
        else:
            tiers.append([k])
            leader = k

    # Too many tiers: merge the adjacent pair with the smallest gap
    while len(tiers) > max_tiers:
        gaps = [
            min(theta[k] for k in tiers[t]) - max(theta[k] for k in tiers[t + 1])
            for t in range(len(tiers) - 1)
        ]
        t = int(np.argmin(gaps))
        tiers[t] = tiers[t] + tiers[t + 1]
        del tiers[t + 1]
    return tiers


# --------------------------------------------------------------------------
# Matchup selection
# --------------------------------------------------------------------------
def choose_next_pair(n, theta, Sigma, asked):
    """Return (i, j, priority) or None. i is shown as A, j as B."""
    sd = np.sqrt(np.diag(Sigma))
    best_floor = np.max(theta - 2 * sd)
    contender = (theta + 2 * sd) >= best_floor

    # For large lists, restrict to neighbours in the ranking (plus unseen items).
    restrict = n > 100
    if restrict:
        order = np.argsort(-theta)
        rank = np.empty(n, dtype=int)
        rank[order] = np.arange(n)
        seen = np.zeros(n, dtype=bool)
        for (_i, _j) in asked:
            seen[_i] = True
            seen[_j] = True

    candidates = []
    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) in asked:
                continue
            if not (contender[i] or contender[j]):
                continue
            if restrict and abs(rank[i] - rank[j]) > 5 and seen[i] and seen[j]:
                continue
            candidates.append((misorder(theta, Sigma, i, j), i, j))

    if not candidates:
        return None

    best = max(c[0] for c in candidates)
    pool = [c for c in candidates if c[0] >= best - TIE_BAND]
    prio, i, j = random.choice(pool)
    if random.random() < 0.5: # randomise left/right display
        i, j = j, i
    return i, j, prio


def should_stop(n, num_asked, next_pair):
    if n <= 1:
        return True
    total_pairs = n * (n - 1) // 2
    cap = min(total_pairs, math.ceil(CAP_MULT * n))
    floor = min(total_pairs, math.ceil(FLOOR_MULT * n))
    if num_asked >= cap:
        return True
    if next_pair is None:
        return True
    if num_asked < floor:
        return False
    return next_pair[2] < STOP_PRIORITY



CHOICES_FILE = '/choices.txt'
def main(items):
    if not items:
        dir.ensure_exists(CHOICES_FILE)
        edit_file((CHOICES_FILE,), extra="\nPut all options on new lines")
        choices = dir.cat((CHOICES_FILE,))
        if choices is None:
            return
        items = choices.split('\n')

    items = [t for i in items if (t := i.strip())]
    if len(items) == 0:
        print("\033[91mNo items!\033[0m")
        return

    wp = WrapPrinter()
    mxitln = max(len(i) for i in items)
    mxmidln = 2
    colln = mxitln * 2 + 2 + mxmidln
    boxed = ['┌─'+'─'*colln+'─┐']
    end = '\n└─'+'─'*colln+'─┘'

    n = len(items)
    comparisons = []
    asked = set()
    theta = np.zeros(n)
    Sigma = np.eye(n) / LAMBDA
    try:
        while True:
            theta, Sigma = fit(
                n, comparisons, theta
            )
            _next = choose_next_pair(n, theta, Sigma, asked)
            if should_stop(n, len(comparisons), _next):
                break
            i, j = _next[0], _next[1]
            a, b = items[i], items[j]
            wp('\n'.join(boxed)+f'{end}\n{a} vs {b}\n>>  >   <  <<    quit\n1   2   3   4     q')
            while True:
                choice = wait("", wait_for="1234q")
                if len(choice) == 1 and choice in '1234':
                    c = int(choice)-1
                    comparisons.append((i, j, Y[c]))
                    asked.add((min(i, j), max(i, j)))
                    txt = ['>>', '>', '<', '<<'][c]
                    boxed.append(f"│ {a.ljust(mxitln)} {txt.center(mxmidln)} {b.rjust(mxitln)} │")
                    break
                elif choice == "q":
                    raise KeyboardInterrupt()
                # elif choice == "u":
                #     if comparisons:
                #         i, j, _ = comparisons.pop()
                #         asked.discard((min(i, j), max(i, j)))
                #     break
    finally:
        wp('\n'.join(boxed)+end)
        print("\nResults:\033[K")
        scores = final_scores(theta)

        mxitln = max(mxitln, 4) # Include "Item" title
        print('╔═'+'═'*5+'═╦═'+'═'*mxitln+'═╗')
        print(f"║ Score ║ {"Item".ljust(mxitln)} ║")
        print('╠═'+'═'*5+'═╬═'+'═'*mxitln+'═╣')
        for item, score in sorted(zip(items, scores), key=lambda t: -t[1]):
            print(f"║ {score:5.1f} ║ {item.ljust(mxitln)} ║")
        print('╚═'+'═'*5+'═╩═'+'═'*mxitln+'═╝')


        print("\nTier list:")
        for t, members in enumerate(make_tiers(theta, Sigma)):
            print(f"  {TIER_LABELS[t] if t < len(TIER_LABELS) else str(t + 1)}")
            last = len(members)-1
            for i, k in enumerate(sorted(members, key=lambda k: -theta[k])):
                print(f"  {'└' if i == last else '├'}─ {items[k]} ({round(scores[k], 1)})")
