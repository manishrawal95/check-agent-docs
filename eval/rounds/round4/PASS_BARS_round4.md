# Round 4 pass bars (v0.5)

Written 2026-10-22 after freezing ctxlint 0.5.0 (`FROZEN_v0.5.md5`) and before v0.5 ran on any round 4 repo.
The round 4 repo list is chosen after this file is written.

**Product under test:** `ctxlint` 0.5.0 in review mode. Stage 1 runs as shipped. Stage 2 runs on the packets
ctxlint writes, answered by Claude Haiku following `REVIEW_INSTRUCTIONS`, reading only the packet (as the API call would).
The review stage only sees files ctxlint selects (`needs_review`), as shipped.

**Truth:** an independent reviewer (Opus) checks every reported issue against the repository. Recall: a blind audit
of a random sample of repos by independent reviewers, then every audit claim re-verified by a second reviewer.

Same bars as round 3, so the two rounds compare directly:

| # | Bar | Pass if |
|---|-----|---------|
| 1 | Precision: reported issues confirmed real (all repos) | at least 90% |
| 2 | Precision in the audited repos | at least 90% |
| 3 | Recall on existence claims (paths, folders, files, scripts, targets, tasks, package manager) | at least 70% |
| 4 | Recall on all checkable claims (including what commands do) | at least 50% |
| 5 | Median stage-1 time per repo | under 5 seconds |

Also reported: facts-only mode precision (every facts-only finding verified too), and suggested-fix accuracy.
