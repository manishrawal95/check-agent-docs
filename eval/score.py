"""Score a round against its pass bars.

Usage: python3 eval/score.py <out_dir> <audit_sample.txt>
Needs in <out_dir>: review_issues.json, factsonly_issues.json, verdicts_review*.jsonl, verdicts_factsonly*.jsonl,
audit_claims.json (merged blind audit, each with "aid") and verified_audit*.jsonl (second-reviewer verdicts).
Recall: an audit claim verified "wrong" counts as found if a confirmed check-agent-docs issue is in the same repo and file,
within 1 line, quoting overlapping text. Confirmed check-agent-docs issues in audited repos that the audit missed are added
to both numerator and denominator.
"""
import glob, json, re, statistics, sys
from collections import Counter
from pathlib import Path

out = Path(sys.argv[1]); sample = set(open(sys.argv[2]).read().split())
def load(pattern):
    d = {}
    for f in glob.glob(str(out / pattern)):
        for l in open(f):
            if l.strip():
                x = json.loads(l); d[x.get("vid") or x.get("aid")] = x
    return d
vr, vf, va = load("verdicts_review*.jsonl"), load("verdicts_factsonly*.jsonl"), load("verified_audit*.jsonl")
rev = json.load(open(out / "review_issues.json"))
for i in rev:
    i["verdict"] = vr[i["issue_id"]]["verdict"]
conf = [i for i in rev if i["verdict"] == "confirmed"]
pa = [i for i in rev if i["repo"] in sample]
print(f"1. precision, all repos: {len(conf)}/{len(rev)} = {len(conf) / max(1, len(rev)):.1%}")
print(f"2. precision, audited repos: {sum(i['verdict'] == 'confirmed' for i in pa)}/{len(pa)}")
claims = json.load(open(out / "audit_claims.json"))
wrong = [c for c in claims if va.get(c["aid"], {}).get("verdict") == "wrong"]
toks = lambda s: {t.strip("`/.,()#") for t in re.split(r"\s+", s) if len(t.strip("`/.,()#")) > 2}
def match(c, i):
    return c["repo"] == i["repo"] and c["file"] == i["file"] and abs(c["line"] - i["line"]) <= 1 and (
        c["claim"] in i["claim"] or i["claim"] in c["claim"] or bool(toks(c["claim"]) & toks(i["claim"])))
found, used = set(), set()
for c in wrong:
    for i in conf:
        if match(c, i):
            found.add(c["aid"]); used.add(i["issue_id"])
extra = [i for i in conf if i["repo"] in sample and i["issue_id"] not in used]
ex_extra = [i for i in extra if i["kind"] != "other"]
for n, (t, ex) in enumerate((("existence", ex_extra), (None, extra)), 3):
    w = [c for c in wrong if t is None or va[c["aid"]]["type"] == t]
    f = sum(c["aid"] in found for c in w) + len(ex)
    print(f"{n}. recall, {t or 'all claims'}: {f}/{len(w) + len(ex)} = {f / max(1, len(w) + len(ex)):.1%}")
times = json.load(open(out / "stage1_times.json"))
print(f"5. stage-1 time: median {statistics.median(times.values()):.3f}s, max {max(times.values()):.2f}s")
fo = json.load(open(out / "factsonly_issues.json"))
print(f"facts-only precision: {sum(vf[i['issue_id']]['verdict'] == 'confirmed' for i in fo)}/{len(fo)}")
fx = [vr[i["issue_id"]].get("fix_correct") for i in conf if i.get("suggested_fix")]
print(f"suggested fixes correct on real issues: {fx.count(True)}/{len(fx)}")
for c in wrong:
    if c["aid"] not in found:
        print(f"  miss {c['aid']} [{va[c['aid']]['type']}] {c['repo']} {c['file']}:{c['line']} {c['claim'][:60]}")
