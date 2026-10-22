"""Run a frozen ctxlint on a list of repos and write review packets exactly as the product would.

Usage: python3 eval/emit_packets.py <frozen ctxlint.py> <repos_dir> <repo list> <out_dir>
Writes <out_dir>/<repo>/*.packet.txt + .facts.json, <out_dir>/review_list.txt (found with os.walk, so
dot-files are included: a shell glob dropped 15 files in round 4), <out_dir>/factsonly_issues.json and
<out_dir>/stage1_times.json.
"""
import hashlib, importlib.util, json, os, re, statistics, subprocess, sys, time
from pathlib import Path

frozen, repos_dir, listfile, out = sys.argv[1:5]
spec = importlib.util.spec_from_file_location("frozen", frozen)
c = importlib.util.module_from_spec(spec); sys.modules["frozen"] = c; spec.loader.exec_module(c)
out = Path(out); out.mkdir(parents=True, exist_ok=True)
repos = [l.split("\t")[0].strip().replace("/", "_") for l in open(listfile) if l.strip()]
times, facts_only = {}, []
for rn in repos:
    root = Path(repos_dir) / rn
    if not root.is_dir():
        print("missing repo", rn); continue
    t0 = time.perf_counter()
    repo = c.Repo(root); F = c.Facts(repo); sel = []
    for f in c.context_files(repo):
        text = repo.read(f, committed_fallback=True) or ""
        if c.is_template(f, text):
            continue
        fs = c.check(repo, F, f, text)
        if c.needs_review(fs) and len(c.split_lines(text)) <= c.MAX_PACKET_LINES:
            sel.append((f, text, fs))
    times[rn] = time.perf_counter() - t0
    for f, text, fs in sel:
        name = re.sub(r"[^A-Za-z0-9_.-]", "__", f) + "." + hashlib.sha1(f.encode()).hexdigest()[:6]
        d = out / rn; d.mkdir(exist_ok=True)
        (d / f"{name}.packet.txt").write_text(c.packet(repo, F, f, text, fs))
        (d / f"{name}.facts.json").write_text(json.dumps([c.asdict(x) for x in fs]))
    p = subprocess.run([sys.executable, frozen, str(root), "--no-llm", "--format", "json"], capture_output=True, text=True,
                       env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": os.environ.get("HOME", "/tmp")})
    for i in json.loads(p.stdout)["issues"]:
        i["repo"] = rn; facts_only.append(i)
for n, i in enumerate(facts_only):
    i["issue_id"] = f"f{n:03d}"
packets = sorted(str(Path(dp, fn).resolve()) for dp, _, fns in os.walk(out) for fn in fns if fn.endswith(".packet.txt"))
(out / "review_list.txt").write_text("\n".join(packets) + "\n")
(out / "factsonly_issues.json").write_text(json.dumps(facts_only, indent=1))
(out / "stage1_times.json").write_text(json.dumps(times))
print(f"{len(repos)} repos, {len(packets)} packets, {len(facts_only)} facts-only issues, "
      f"median stage-1 {statistics.median(times.values()):.3f}s, max {max(times.values()):.2f}s")
