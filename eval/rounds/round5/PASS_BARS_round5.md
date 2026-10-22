# Round 5 pass bars (v0.5.2)

Written 2026-10-22 after freezing ctxlint 0.5.2 (`FROZEN_v0.5.2.md5`, md5 da145f7b2ba008b5ee3a562e6f8bd1e7) and before 0.5.2 ran on any round 5 repo.

**Repos.** Candidates are in `candidates_round5_fresh.txt`: well-known public repos, minus every repo used in rounds 1–4. They were cloned at their current HEAD, and every candidate with at least one instruction file ctxlint reads is in the round (`inventory_round5.txt`, 95 repos). The candidates were cloned and counted before this version was final, but no ctxlint output on them has been looked at.

**Audit sample.** 30 repos drawn with `random.Random(5).sample(sorted(repos), 30)`.

**Product under test.** ctxlint 0.5.2 in review mode, exactly as shipped:
- Stage 1 runs as shipped.
- Template files are skipped.
- The review only sees files `needs_review` selects. Packets are listed with `find` so names starting with a dot are included; round 4 lost 15 files to a shell glob.
- Stage 2 is answered by Claude Haiku following `REVIEW_INSTRUCTIONS` (prompt version 6), reading only the packet, as the API call would.

**Truth.**
- Precision: every reported issue is checked by an independent Opus reviewer against the repository (`VERIFY_PROMPT.md`).
- Recall: blind audit of the 30 sample repos by independent Opus reviewers. Then every audit claim is re-verified by a second reviewer.

Same bars as rounds 3 and 4:

| # | Bar | Pass if |
|---|-----|---------|
| 1 | Precision: reported issues confirmed real (all repos) | at least 90% |
| 2 | Precision in the audited repos | at least 90% |
| 3 | Recall on existence claims (paths, folders, files, scripts, targets, tasks, package manager) | at least 70% |
| 4 | Recall on all checkable claims (including what commands do) | at least 50% |
| 5 | Median stage-1 time per repo | under 5 seconds |

Also reported: facts-only mode precision (every facts-only finding verified), and suggested-fix accuracy.
