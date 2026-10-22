# Round 2 pass bars (written before running on any round 2 repo)

Set 2026-10-22, after round 1 and before the checker (v2, md5 `93a91036...`) or judge (v2) saw any round 2 repo.

Changes since round 1, all decided from round 1 dev data:
- Checker v2 fixes two bugs that round 1 showed were real: justfile recipes with arguments, and case-insensitive paths. It also reports "same name found at" for likely moved files.
- Judge v2 counts moved or renamed files as real problems and suggests the new path.

**Sample:** fresh public repos, none of them used in round 1: every public Anthropic repo that has an agent context file, plus mid-size SaaS and AI-tool repos (`candidates_round2.txt`).

**Truth:** an independent reviewer (Opus) checks every checker flag against the repo. I re-check a sample by hand.

| # | Bar | Pass if |
|---|-----|---------|
| 1 | Repos with at least one confirmed wrong claim | at least 30% |
| 2 | Precision of the full product (checker + judge): kept flags that are confirmed real | at least 90% |
| 3 | Real problems the judge keeps, out of all confirmed problems the checker found | at least 80% |
| 4 | Median checker time per repo | under 5 seconds |

**Recall audit (no bar, reported only):** for the Anthropic repos, the reviewer reads every agent context file in full and lists every checkable wrong claim, so we can see what the checker misses.
