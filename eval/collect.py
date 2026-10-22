"""Turn reviewer answers into the issues check-agent-docs would report, and build verification inputs.

Usage: python3 eval/collect.py <frozen check_agent_docs.py> <repos_dir> <out_dir> <answers.jsonl>...
answers lines: {"packet": "<packet path>", "issues": [...]}. Every packet in review_list.txt must be answered.
Writes <out_dir>/review_issues.json and verify_review.jsonl / verify_factsonly.jsonl (inputs for prompts/VERIFY_PROMPT.md).
"""
import importlib.util, json, subprocess, sys
from pathlib import Path

frozen, repos_dir, out = sys.argv[1:4]; out = Path(out)
spec = importlib.util.spec_from_file_location("frozen", frozen)
c = importlib.util.module_from_spec(spec); sys.modules["frozen"] = c; spec.loader.exec_module(c)
todo = set(l.strip() for l in open(out / "review_list.txt") if l.strip())
done, issues = set(), []
for af in sys.argv[4:]:
    for l in open(af):
        if not l.strip():
            continue
        d = json.loads(l); p = d["packet"]
        if p in done:
            continue
        done.add(p); repo = Path(p).parent.name
        cf = open(p).readline().split("INSTRUCTION FILE: ")[1].strip()
        fs = [c.Fact(c.Mention(**x["mention"]), x["status"], x["note"], x["moved_to"])
              for x in json.load(open(p.replace(".packet.txt", ".facts.json")))]
        text = c.Repo(Path(repos_dir) / repo).read(cf, committed_fallback=True) or ""
        for i in c.review_issues(cf, {"issues": d.get("issues", [])}, fs, text):
            x = dict(i.__dict__); x["repo"] = repo; issues.append(x)
missing = todo - done
print(f"answered {len(todo & done)} of {len(todo)}" + (f"; UNANSWERED: {len(missing)}" if missing else ""))
for n, x in enumerate(issues):
    x["issue_id"] = f"r{n:03d}"
(out / "review_issues.json").write_text(json.dumps(issues, indent=1))

def verify_rows(items):
    rows = []
    for x in items:
        d = Path(repos_dir) / x["repo"]
        txt = subprocess.run(["git", "-C", str(d), "show", f"HEAD:{x['file']}"], capture_output=True, text=True).stdout
        lines = txt.split("\n"); lo = max(0, x["line"] - 5)
        rows.append({"vid": x["issue_id"], "repo": x["repo"], "file": x["file"], "line": x["line"], "claim": x["claim"],
                     "reported_problem": x["problem"], "suggested_fix": x["suggested_fix"],
                     "surrounding_text": "\n".join(f"{i + 1}| {lines[i]}" for i in range(lo, min(len(lines), x["line"] + 3))),
                     "repo_file_list": f"{d}.tree", "repo_dir": str(d)})
    return rows

(out / "verify_review.jsonl").write_text("\n".join(json.dumps(r) for r in verify_rows(issues)) + "\n")
fo = json.load(open(out / "factsonly_issues.json"))
(out / "verify_factsonly.jsonl").write_text("\n".join(json.dumps(r) for r in verify_rows(fo)) + "\n")
print(f"{len(issues)} review issues, {len(fo)} facts-only issues to verify")
