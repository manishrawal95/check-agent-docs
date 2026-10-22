# Round 3 pass bars (v3, full-file review)

Written 2026-10-22 after freezing ctxlint v3 (md5 in `FROZEN_v3.md5`) and before running v3 on any round 3 repo.

Disclosure: the independent recall audit of the 30-repo sample finished while I was making the last
facts-only-mode change. I saw its summaries (44 wrong claims, some about what scripts do rather than
whether things exist). No change to v3 was made because of them. Bar 4 was set knowing that some audit
claims are out of v3's reach, which makes it harder to pass, not easier.

**Sample:** 61 fresh repos with agent instruction files, none used in rounds 1-2 or in v3 development
(`round3_repos.txt`). Recall sample: 30 of them drawn at random (seed 2026) from those with 6 or fewer
instruction files (`round3_audit_sample.txt`), audited blind by independent reviewers (`audit_r3/`).

**Product under test:** `ctxlint` in review mode. Stage 1 runs as shipped. Stage 2 runs on the packets
ctxlint writes, answered by Claude Haiku following `REVIEW_INSTRUCTIONS`, reading only the packet
(no repository access), which matches what the API call sees.

**Truth:** an independent reviewer (Opus) checks every issue v3 reports against the repository.
Recall denominator = audit claims confirmed wrong ∪ v3 issues the reviewer confirms, in the 30 audited repos.

| # | Bar | Pass if |
|---|-----|---------|
| 1 | Precision: reported issues confirmed real (all 61 repos) | at least 90% |
| 2 | Precision in the 30 audited repos | at least 90% |
| 3 | Recall on existence claims (paths, folders, files, scripts, targets, package manager) | at least 70% |
| 4 | Recall on all checkable claims (including what scripts do, counts) | at least 50% |
| 5 | Median stage-1 time per repo | under 5 seconds |

Also reported (no bar): facts-only mode precision; review tokens per instruction file.
