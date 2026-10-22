"""Regression: are known real problems still flagged as missing facts?

Usage: python3 eval/regress.py <old check_agent_docs.py> <new check_agent_docs.py> <repos_dir> [<repos_dir> ...]
Runs check() from both versions on every instruction file of every repo found in the repos dirs that appears in
data/known_real_problems.json or the round lists, then compares.
"""
import importlib.util, json, statistics, sys, time
from pathlib import Path

here = Path(__file__).parent
truth = {tuple(x) for x in json.load(open(here / "data/known_real_problems.json"))}

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); sys.modules[name] = m; spec.loader.exec_module(m); return m

def run(mod, dirs):
    missing, times, errors = set(), [], []
    for d in dirs:
        for root in sorted(Path(d).iterdir()):
            if not (root / ".git").exists():
                continue
            t0 = time.perf_counter()
            try:
                repo = mod.Repo(root); facts = mod.Facts(repo)
                for f in mod.context_files(repo):
                    for x in mod.check(repo, facts, f, repo.read(f, committed_fallback=True) or ""):
                        if x.status == "missing":
                            missing.add((root.name, f, x.mention.line))
            except Exception as e:
                errors.append(f"{root.name}: {e!r}")
            times.append(time.perf_counter() - t0)
    return missing, times, errors

old, new = load("old", sys.argv[1]), load("new", sys.argv[2])
mo, to, eo = run(old, sys.argv[3:])
mn, tn, en = run(new, sys.argv[3:])
print(f"repos: {len(tn)}; errors old {len(eo)} new {len(en)}")
for e in en:
    print("  ERROR", e)
print(f"known real problems flagged: old {len(truth & mo)}, new {len(truth & mn)} (of {len(truth)})")
for x in sorted((truth & mo) - mn):
    print("  LOST", x)
print(f"missing facts: old {len(mo)}, new {len(mn)}")
print(f"stage-1 median: old {statistics.median(to):.3f}s, new {statistics.median(tn):.3f}s; max new {max(tn):.2f}s")
sys.exit(1 if (truth & mo) - mn or en else 0)
