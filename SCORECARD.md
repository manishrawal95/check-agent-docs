# Gate 1 scorecard: context linter (ctxlint)

Data behind rounds 4 and 5 (issues, verdicts, audit claims, pass bars, md5s) is in `eval/rounds/`. Repo lists for every round are in `eval/data/`. File names mentioned below refer to those folders.

Run on 2026-10-22. Pass bars were written in `PASS_BARS.md` before the checker ran on any repo.

## Result

| Bar | Pass if | Checker alone (frozen) | Result |
|---|---|---|---|
| 1. Repos with a confirmed wrong claim | at least 30% | 15 of 92 (16.3%) | **Fail** |
| 2. Precision on held-out repos | at least 90% | 13 of 44 (29.5%) | **Fail** |
| 3. Median time per repo | under 5 s | 0.04 s (max 1.4 s) | **Pass** |

**Not passed as written.** The deterministic checker finds real problems, but most of its flags were false alarms that pattern-matching can't tell apart. Typical cases are examples, files in other repos, gitignored folders, and files the reader is told to create.

A two-stage version, added after the bars failed, fixed precision:

| Two-stage (checker, then a Haiku judge) | Dev repos | Held-out repos |
|---|---|---|
| Flags kept | 19 | 8 |
| Confirmed real | 19 (100%) | 8 (100%) |
| Real problems kept | 19 of 22 | 8 of 13 |

**Treat the two-stage numbers as promising, not proven.** The judge prompt was written after reading the held-out reviewer's list of false-alarm causes, so held-out is no longer clean for it. It needs a fresh set of repos.

## Data
- 105 popular public repos, cloned at their default branch on 2026-10-22 (`candidates.txt`). 92 had at least one agent context file (`inventory.txt`).
- The repo list was chosen from memory and leans toward large, well-maintained projects, where drift should be lowest. dub-inc/dub failed to clone.
- The repos were split alphabetically before tuning: 48 dev repos (up to `lobehub`) and 44 held-out repos (`split_*.txt`). The checker was tuned only on dev flags, then frozen (md5 `3be8f1b0...`, `FROZEN_CHECKER.md5`) before it ran on held-out.

## How flags were judged
- An independent reviewer (Opus) checked each of the 99 flags against the repo's full file list, its package.json files, Makefiles and justfiles (`review/verdicts_*.jsonl`).
- I re-checked 8 of its calls by hand: bun, pydantic-ai, prisma, cline, cal.com, langchainjs, transformers and excalidraw-mcp. All 8 matched.

## What the real problems look like
35 problems were confirmed across 15 repos, all in actively maintained projects. Most are files or folders that moved:

| Repo | Instruction file says | Reality |
|---|---|---|
| oven-sh/bun | `src/shell/`, `src/bake/` | both moved under `src/runtime/` |
| pydantic/pydantic-ai | `tests/menu_script.py` | moved to `tests/clai2/` |
| PostHog/posthog | `utils/reportMembership.ts` | moved to `packages/core/src/inbox/` |
| cline/cline | `src/core/slash-commands/index.ts` | `src/` moved to `apps/vscode/src/`, and the file is gone |
| langchain-ai/langchainjs | `libs/langchain-standard-tests/` | now `internal/standard-tests/` |
| apache/airflow | `tests/cli/test_cli_parser.py` | now under `airflow-core/tests/unit/cli/` |
| calcom/cal.com | `packages/features/ee/workflows/lib/constants.ts` | not found anywhere |
| huggingface/transformers | `make fixup` | no such target; the closest are `style` and `fix-repo` |
| excalidraw/excalidraw-mcp | `npm install` | repo uses pnpm (lockfile and `packageManager`) |

Each of these sends an agent to a file, folder or command that isn't there.

## Why the checker alone failed
Per the independent reviewer, false alarms fell into these groups:
- **Another place:** external packages, other repos, upstream projects, or users' own projects (about 25)
- **Examples and placeholders:** naming patterns, `skill-name/...` (about 12)
- **Gitignored or generated:** `.cursor/rules` gitignored in prisma, runtime outputs (about 15)
- **Text says it's gone:** "dependabot.yml was deleted" (3)
- **Checker bugs:** a case-sensitive match missed a template that exists; just recipes that do exist (3)

All of these come down to the intent behind the text, which the AI judge read correctly.

## What the two-stage version still misses
- 5 held-out and 3 dev problems were dropped by the judge. Most were moved files, because the prompt said a "nested location the text clearly means" counts as existing.
- The fix: a moved file should count as `real`, with the new path as an auto-fix.

## What this means
1. **The problem is real, even in the best-run repos.** 15 of 92 top projects, including bun, PostHog, airflow, vscode and pydantic-ai, have agent instructions pointing at things that aren't there. The rate in ordinary company repos is unknown and likely higher.
2. **Regex alone can't do this job; regex plus a cheap model can.** That's the product design: a fast local scan, then a small model judging intent, then an auto-fix with the new path.
3. **Moved files are the most common real problem.** That makes "here's where it went" the core feature.
4. **Bar 1 (30%) wasn't reached.** This sample is biased toward large, careful projects, and the checker deliberately skips anything doubtful. Recall wasn't measured.

## Next test (round 2)
- 50 or more fresh repos the checker and judge have never seen, including smaller and mid-size SaaS repos.
- Judge prompt fixed so moved files count as `real` with a suggested path.
- Same bars. Also measure recall, by having the reviewer read 20 context files end to end and list every wrong claim.

## Re-run
```
python3 ctxlint.py /path/to/repo            # on a normal checkout
python3 ctxlint.py REPO --tree-file REPO.tree --json
python3 score.py                            # checker-alone bars, from review/verdicts_*.jsonl
```

---

# Round 2: fresh repos, including Anthropic's

Run on 2026-10-22. Pass bars were written in `PASS_BARS_round2.md` before checker v2 (md5 `93a91036...`) or judge v2 saw any round 2 repo.

**Changes from round 1:**
- Checker v2 fixes the justfile and letter-case bugs, and reports "same name found at" for moved files.
- Judge v2 counts moved files as real and suggests the new path.

**Sample:**
- 94 fresh repos were cloned, with no overlap with round 1. Three duplicates were removed: two were redirects (anthropic-cookbook → claude-cookbooks, dxt → mcpb), and anomalyco/opencode is the same code as round 1's sst/opencode.
- Of the 91 left, 63 have agent context files. 9 of those are Anthropic repos.
- The rest are mid-size SaaS and AI tools (coolify, activepieces, plane, CopilotKit, clerk, langfuse and others) plus a few large ones (jest, pnpm).

## Result

| Bar | Pass if | Result |
|---|---|---|
| 1. Repos with a confirmed wrong claim | at least 30% | 12 of 63 (19.0%), **fail** |
| 2. Precision of checker plus judge | at least 90% | 48 of 54 (88.9%), **fail, just short** |
| 3. Real problems the judge keeps | at least 80% | 48 of 48 (100%), **pass** |
| 4. Median checker time per repo | under 5 s | 0.04 s, **pass** |

- The checker alone was right on 48 of 126 flags (38%).
- The independent reviewer marked 1 flag as unclear. It is excluded from both counts.

## What the 6 false alarms were
- **claude-cookbooks:** `docs/` is ignored by a nested `skills/.gitignore` that the judge didn't read. Fix: the checker should apply every `.gitignore` itself.
- **CopilotKit `.meridian/` (3 flags):** a local tool folder. It is gitignored in sibling folders but not in this one. This is a borderline call.
- **Infisical (2 flags):** shorthand paths for files that exist deeper in the tree.

## Checker-only false alarms the judge correctly removed
- **ToolJet (34 flags):** `server/ee` and `frontend/ee` are git submodules pointing at a private repo. Fix: the checker should skip paths inside submodules.
- **pnpm (6 flags):** `pnpm change` and `pnpm lane` are built-in commands. Fix: read pnpm's own command list.

## Confirmed problems (hand-checked sample)

| Repo | Instruction file says | Reality |
|---|---|---|
| coollabsio/coolify | a whole `.ai/` doc tree (16 references) | only `.ai/lessons.md` is tracked |
| inngest/inngest-js | `src/components/InngestMiddleware.ts` | gone; middleware now lives in `src/components/middleware/` |
| jestjs/jest | `e2e/__tests__/configFile.test.ts` | doesn't exist (`config.test.ts` does) |
| QwenLM/qwen-code | `npm install` | repo uses pnpm 11 |

## Anthropic repos: full audit
The reviewer read all 27 agent context files in 12 Anthropic repos (9 from round 2 plus the 3 SDK repos from round 1) and listed every checkable wrong claim. I re-checked each one by hand.

| Repo (commit) | File | Claim | Reality | Status |
|---|---|---|---|---|
| anthropic-sdk-csharp (`027b132`, 2026-10-21) | `CLAUDE.md:11` | a new package needs entries in `release-please-config.json` | no such file; only `.release-please-manifest.json` exists | **Real** |
| claude-agent-sdk-demos (`826b268`, 2026-03-13) | `simple-chatapp/CLAUDE.md:38` | `client/hooks/useWebSocket.ts` | no `hooks/` folder in `simple-chatapp/client/`; the file exists in `email-agent/`, so the structure looks copied | **Real** |
| claude-code-base-action (`5c926fa`, 2026-10-22) | `CLAUDE.md:52` | `.github/workflows/test-base-action.yml` | this is an automated mirror with no `.github/`; the file exists in claude-code-action, the source repo | Mirror artifact, not a bug at the source |
| claude-cookbooks | `skills/CLAUDE.md:15` | "MUST use local whl" | no `.whl` tracked | Medium confidence; may be a local-only file |
| claude-cookbooks | `skills/CLAUDE.md:177` | `docs/skills_cookbook_plan.md` | gitignored by `skills/.gitignore` | **Not a bug.** I wrongly called this real in chat before the review |

The other 22 files had nothing checkably wrong. Paths, scripts, make targets and package managers all matched.

**Recall on Anthropic repos:** the audit found 3 strong issues. The checker flagged only 1 of them, the mirror artifact. It missed the C# one because it skips bare filenames by design, and the demos one because it doesn't parse folder-tree diagrams. Recall is the weak point.

## What round 2 means
1. **The two-stage design almost holds on fresh data:** 89% precision and 100% kept, with no tuning on these repos. The remaining false alarms come from two fixable gaps (nested `.gitignore` files and submodules) plus one borderline call.
2. **Bar 1 failed in both rounds:** about 16 to 19% of repos have a confirmed problem, below the 30% guess. The finding is now consistent: roughly 1 in 6 popular repos with agent files point agents at things that aren't there. That is useful, but smaller than assumed.
3. **Recall is the real gap.** Full reading found problems the checker structurally can't see: bare filenames, tree diagrams, and claims that need judgment (the whl). The best product is probably the judge reading the whole file with the repo's file list, not just judging checker flags.

## Next steps
- Checker: apply all `.gitignore` files, skip paths inside submodules, read pnpm's built-in commands, and parse tree diagrams. Bare filenames can go to the judge instead of being dropped.
- Test a full-file judge mode for recall on a fresh set, measured against a full audit like the one above.

---

# Round 3: v3 (full-file review), fresh repos, precision and recall

Run on 2026-10-22. ctxlint v3 was frozen (`FROZEN_v3.md5`) and the bars were written (`PASS_BARS_round3.md`) before v3 ran on any round 3 repo.

**What changed in v3:**
- Stage 1 now extracts far more: bare file names, prose paths, folder-tree diagrams, and paths after runners.
- It checks every `.gitignore` with git, skips submodules, and uses the nearest lockfile.
- Stage 2 reads each whole instruction file next to those facts. Files where every claim checked out are never sent to the model.

**Sample:**
- 61 fresh repos with instruction files: 479 instruction files, of which 167 needed review.
- Recall sample: 30 of the 61, drawn at random with seed 2026, audited blind by independent reviewers.
- The audit was then re-verified claim by claim. The original audit was wrong on 4 of 44 claims, leaving 40 as ground truth.

**How stage 2 ran here:** Claude Haiku answered the exact packets ctxlint writes, reading only the packet with no repository access, which is what the API call sees. The API code path itself was not exercised, because this workspace has no API key.

## Result: failed 4 of 5 bars

| Bar | Pass if | Result |
|---|---|---|
| 1. Precision, all repos | at least 90% | 78 of 87 (89.7%), **fail** |
| 2. Precision, audited repos | at least 90% | 18 of 22 (81.8%), fail |
| 3. Recall, existence claims | at least 70% | 16 of 37 (43.2%), **fail** |
| 4. Recall, all claims | at least 50% | 16 of 43 (37.2%), fail |
| 5. Stage-1 time per repo | under 5 s | median 0.06 s, max 2.4 s, pass |

- Recall uses the corrected audit: 34 existence claims plus 6 about behaviour or counts. It also counts 3 real problems v3 found that the audit missed.
- 34 issues came with a suggested fix. Reviewers judged 30 correct and 1 wrong, and left 3 without a call.

**The 9 false alarms:**
- `include Makefile.frontend` wasn't followed (4)
- raycast authors deliberately using bun despite an npm lockfile (3)
- Text that itself said the folder doesn't exist (1)
- Steps meant for another repo's clone (1)

**The 21 existence misses:**
- Case-only matches counted as found (10)
- Section-scoped claims (4)
- Bare folder names not extracted (3)
- Paths after `pytest` not extracted (3)
- `.github/` files resolved against `.github/` instead of the repo root (2)

Those add up to 22, one more than the 21 misses, because one SuperClaude claim is counted under two causes.

## v3.1: fixes, dev re-run on already-seen repos (not a clean test)

**Fixes in v3.1:**
- Case-only matches are reported, because they break on Linux.
- Paths after test and lint tools are extracted.
- Bare folder names like `routers/` are extracted.
- Paths in `.github/` and `.cursor/` instruction files resolve from the repo root.
- `Makefile.*` and included makefiles are read.
- Text saying something "does not exist" is honoured.
- Symlinked CLAUDE.md → AGENTS.md is reviewed once.
- Lockfiles by folder are listed for the model.

Re-run on the 30 audited repos plus raycast and suna:

| | v3.0 | v3.1 |
|---|---|---|
| Precision (same 32 repos) | 39 of 48 (81.2%) | 40 to 41 of 45 (89 to 91%) |
| Recall, existence claims (audited 30) | 16 of 37 (43.2%) | 20 of 37 (54.1%) |
| Recall, all claims | 16 of 43 (37.2%) | 20 of 43 (46.5%) |

- **Why precision is a range:** one issue (cognee's `pr_lint` without `.yml`) was judged real by one reviewer and shorthand by another.
- **Still missed:**
  - Langflow's 10 case mismatches. The facts were in the packet, but a misleading note was attached. That's now fixed, but untested.
  - github-mcp-server's `pkg/toolsets/`.
  - Two folders the model dropped this time: h3 `test/fixture/` and raycast `media/`.
- **Caveat:** these repos shaped the fixes, so the v3.1 numbers are optimistic. A fresh round 4 is the real test.

## Bottom line after three rounds
- **Precision is close to good:** about 9 in 10 issues ctxlint reports are real, and 30 of the 31 suggested fixes the reviewers ruled on were right.
- **Recall is the gap:** it finds roughly half of what a careful human reviewer finds.
- **The problem is common:** at least 54 of 216 popular repos (25%) have instructions that are wrong at the current commit. With the full review, it was 25 of 61 (41%).

---

# v0.5: bug hunt and hardening (2026-10-22)

**How bugs were found:**
- A new test suite, where each test builds a real git repo.
- An independent code review that reported 20 bugs, 19 of them reproduced.
- A regression run of the old and new versions on all 216 repos from rounds 1 to 3.

About 30 bugs were fixed in total; see `CHANGELOG.md`. The most serious:
- `--fix` could overwrite a whole sentence.
- `--fix` broke CRLF files and couldn't write into dot-folders.
- Any API hiccup crashed the run with the same exit code as "issues found".

**Regression on 216 repos, stage 1:**

| | v3.1 | v0.5 |
|---|---|---|
| Crashes | 0 | 0 |
| Known real problems flagged as missing facts (186 found across all rounds) | 143 | 151 |
| Known real problems lost | n/a | 0 |
| Facts-only findings | 271 | 270 |
| Median time per repo | 0.10 s | 0.10 s |

- The 270 are not the same 270: 41 placeholder findings like `npm run <script>` are gone, and 41 repeated occurrences of known issues were added.
- The regression caught three regressions in early v0.5 drafts before release:
  - Tree entries falling back to the repo root, which lost langflow's case mismatches.
  - Trees giving up when several folders share the root name, which lost sglang.
  - Unreadable Taskfiles making every task look missing.

**Behaviour claims (new):** on the four checkable behaviour claims from the round 3 audit, the review caught two:
- langflow's "`make lint` = mypy"
- supermemory's "`bun run lint` = Next.js lint"

It made no false reports in that check. One of the two misses (nitro's `pnpm typecheck`) is now within reach, because bare `pnpm` and `bun` scripts show their bodies. This is a 4-claim dev check, not a measured rate.

**Still untested:**
- The real Anthropic API call. It is covered only by a fake API server in the tests, including retries, auth errors, bad JSON and caching.

---

# Round 4: v0.5.0 measured on 78 fresh repos (2026-10-22)

**Setup.** ctxlint 0.5.0 was frozen (md5 in `FROZEN_v0.5.md5`) and the pass bars were written (`PASS_BARS_round4.md`) before it ran on any round 4 repo. The 78 repos (`round4_repos.txt`) had never been used before. Stage 2 was answered by Claude Haiku reading only the packets ctxlint writes, as the API call would. Every reported issue was checked by two independent Opus reviewers. For recall, 30 repos were picked at random and audited blind by three Opus reviewers; a second pair re-checked all 88 audit claims and agreed with every one.

## Result: passed 2 of 5 bars

| Bar | Pass if | Result |
|---|---|---|
| 1. Precision, all repos | at least 90% | 46 of 53 (86.8%), **fail** |
| 2. Precision, audited repos | at least 90% | 19 of 20 (95%), pass |
| 3. Recall, existence claims | at least 70% | 18 of 54 (33%), **fail** |
| 4. Recall, all claims | at least 50% | 21 of 89 (24%), **fail** |
| 5. Stage-1 time per repo | under 5 s | median 0.08 s, pass |

- Recall counts one real problem ctxlint found that the audit missed (vinext), so the denominators are 54 and 89.
- Suggested fixes: 21 of 26 correct.
- Facts-only mode (no API key): 14 of 37 correct (38%). This was the weakest result.
- Compared with round 3 (89.7% precision, 43% existence recall), precision held roughly level and recall dropped. This round's audit was much stricter: it found 88 wrong claims in 30 repos, against 43 in round 3, and 35 of them were about what commands do.

**The 7 review false alarms:**
- A template file copied into users' apps (remix, `%%APP_NAME%%`).
- A folder gitignored by a `.gitignore` next to the instruction file (AFFiNE). This was a stage-1 bug.
- Generated, gitignored locale files (authentik).
- Three judgement calls: a Makefile target description, a Jest path pattern that does match, a module reference.
- A private local notes folder (loki).

**The 36 existence misses** (35 diagnosed):
- The review saw a clear "missing" fact and didn't report it: 10.
- Nothing extracted from the line: 12. Three were repo-root paths written with a leading slash (`/src/lib/x.ts`); the rest were package names, class methods, settings and prose.
- Scripts run as `pnpm clean:deps` treated as "may be a binary": 4.
- The file was never sent for review because every extracted claim checked out: 4.
- The path exists, but not where the text says: 4.
- A tox environment: 1.

**Facts-only false alarms (23):** placeholder segments (`internal/vN/`, `make example-N`), Go identifiers (`pkg/errors.CodedError`), extension conventions (`.web.ts/.web.tsx`), paths into other repos or libraries whose folder doesn't exist here at all, and template files.

## 0.5.1: fixes from round 4 and a second bug hunt

**Second bug hunt.** An independent review plus 2,000 fuzzed inputs found 13 bugs, all fixed with tests (details in `CHANGELOG.md`). The most serious:
- `--fix` could write through a symlinked temp file outside the repo.
- A symlink pointing outside the repo could get that file's content sent to the API.
- One Makefile line could make ctxlint run for 100 seconds.
- `--changed` missed renames and accepted refs that git reads as options.

**Fixes from round 4:**
- Stage 1: bare folder names now check the `.gitignore` next to the instruction file.
- Stage 1: leading-slash repo paths are now read, except on lines about URL routes.
- Stage 1: `pnpm x:y` shorthand with a colon now counts as a script.
- Stage 1: `.js` import paths for `.ts` files count as found.
- Facts-only: placeholder, identifier and extension filters added.
- Facts-only: a path is only reported if its top folder exists, it was in the repo's history, or a file of the same name exists elsewhere.
- Both modes: template files (in `template/`, `scaffold/` and similar folders, or with `%%NAME%%` markers) are skipped entirely.

**Dev check (not a clean test: the fixes were made after seeing round 4):**

| | 0.5.0 | 0.5.1 |
|---|---|---|
| Facts-only findings on round 4 repos | 37 (14 real, 38%) | 28 (25 real, 89%) |
| Real facts-only findings lost | n/a | 1 (a deleted folder; would be caught with git history) |
| Known real problems flagged as missing facts (216 older repos) | 151 | 151 |
| Facts-only findings, 216 older repos | 270 | 235 |
| Median stage-1 time | 0.10 s | 0.11 s |

- Of the 28, 13 were verified in round 4. The 12 new ones (Unleash, stack-auth, spotlight, agent-framework) were checked by hand against the repos. All 12 are real.
- Review-mode recall wasn't re-measured. The stage-1 fixes give the reviewer facts for 6 of the 36 misses it couldn't see before.

**Tried and rejected:** adding facts-only findings to review mode when the review drops them. On round 4 that would add 4 real issues and 3 false alarms, and precision would fall from 87% to 83%.

**Correction (found later the same day):** the round 4 numbers above are wrong. They understate ctxlint, so read the corrected section below instead.

---

# Round 4 corrected: a bug in the test setup, not in ctxlint

**What went wrong.** The script that sent packets to the review model listed them with a shell glob, and a glob skips names that start with a dot. So 15 files that ctxlint 0.5.0 would have reviewed were never reviewed:
- `.github/copilot-instructions.md`
- `.cursorrules`
- `.cursor/rules/*`
- `.claude/CLAUDE.md`

All 10 misses described above as "the review saw a clear missing fact and didn't report it" were in those files. Those 15 files were then reviewed exactly as in round 4 (frozen 0.5.0, same prompt, Haiku), and the 13 issues it reported were verified independently. All 13 were real.

| Bar | Pass if | Round 4 as first reported | Round 4 corrected |
|---|---|---|---|
| 1. Precision, all repos | at least 90% | 46 of 53 (86.8%) | 59 of 66 (89.4%), **fail** (just under) |
| 2. Precision, audited repos | at least 90% | 19 of 20 (95%) | 32 of 33 (97%), pass |
| 3. Recall, existence claims | at least 70% | 18 of 54 (33%) | 31 of 54 (57%), **fail** |
| 4. Recall, all claims | at least 50% | 21 of 89 (24%) | 34 of 89 (38%), **fail** |
| 5. Stage-1 time | under 5 s | 0.08 s | 0.08 s, pass |

- Suggested fixes: 24 of 29 correct.
- From round 5 on, packets are listed with `find`, and the bars file says so.

---

# Round 5: v0.5.2 on 95 fresh repos (2026-10-22)

**What changed in 0.5.2, after the corrected round 4:**
- `mise` tasks are read, with their bodies.
- Bare names that exist only in another folder are shown to the review ("FOUND ONLY ELSEWHERE"). Names under a nearby heading such as "**Parser** (`src/parser/`)" are resolved against that folder.
- The review prompt spells out what counts as a wrong description of a command. Examples: the comment says gofumpt but the recipe runs gofmt; it says tox but the task runs nox.
- A new "NOT CHECKED" section lists what stage 1 couldn't settle.

A dev re-run on round 4 looked better: 68 real findings instead of 59, with similar precision once a stage-1 bug was fixed.

**Setup.** Same method as round 4:
- Frozen version (md5 in `FROZEN_v0.5.2.md5`), with bars written before the run (`PASS_BARS_round5.md`).
- 95 repos never used before (`round5_repos.txt`): every candidate with an instruction file.
- Haiku as the review model, reading only packets; all 177 packets were answered.
- Every issue verified by an independent Opus reviewer.
- Blind audit of 30 random repos, with all 42 audit claims re-verified. 36 held up as wrong.

## Result: passed 1 of 5 bars

| Bar | Pass if | Result |
|---|---|---|
| 1. Precision, all repos | at least 90% | 41 of 58 (70.7%), **fail** |
| 2. Precision, audited repos | at least 90% | 7 of 11 (64%), **fail** |
| 3. Recall, existence claims | at least 70% | 6 of 21 (29%), **fail** |
| 4. Recall, all claims | at least 50% | 7 of 36 (19%), **fail** |
| 5. Stage-1 time per repo | under 5 s | median 0.13 s, max 2.7 s, pass |

- Suggested fixes: 18 of 19 correct on real issues.
- Facts-only mode: 21 of 37 (57%). The dev check on round 4 had suggested 89%, so the facts-only filters were fitted to round 4 and don't carry over.

**The 17 review false alarms:**
- `extra_state.cpp/.h` (a file plus its header) read as a folder path: 4. A stage-1 bug.
- The new NOT CHECKED section: 3. It told the reviewer no package depended on "playwright", but `@playwright/test` provides that command.
- The review only saw two of the many packages defining `yarn test`, and the one the table pointed to wasn't among them: 2.
- Judgement calls by the reviewer: 8. Examples: shorthand like "docs/whatsnew", a "files not to modify" list, a folder created at install, a file the docs say is created later, a folder under a heading.

**The 29 misses:**
- Wrong descriptions of commands where ctxlint showed the right script body, but the review didn't report them: 6. Examples: vercel's "ESLint" when `pnpm lint` runs Biome; mui's test and prettier comments; mastra's `dev:playground:full`.
- Claims about tools and config with no command to check: 8. Examples: Mocha + Chai vs Vitest, ESLint rule names in a Biome repo, a pre-commit hook, where CMake writes artifacts.
- Nothing extracted on the line: 11. Examples:
  - Line numbers in code references.
  - A path through a package alias (`@prefect/ui-v2/src/api/mocks`).
  - A Gradle task.
  - Commands in prose.
  - A bold folder name.
  - Editor tasks.
  - A skill name.
- A path accepted because the same path existed in another package: 2.
- `yarn --cwd code test` checked against the root package.json: 1.
- `pnpm vale` (shorthand, not a script) treated as "may be a binary": 1.

## What this means

- The review stage is not stable enough to trust. Precision went from 89% (round 4) to 71% (round 5), and recall ranged from 19% to 57% across the two rounds. Changes that helped on round 4 data hurt on fresh data.
- The weakest link is the small review model. It misses wrong command descriptions even when the evidence is in front of it. It also turns soft hints into false reports.
- The strong part is stage 1 plus suggested fixes. Suggested fixes were right 18 of 19 times. The local checks run in a fraction of a second.

## 0.5.3 (dev, not measured)

Fixes from round 5's false alarms and misses. These are dev changes, and they need a fresh round to count:
- `name.cpp/.h` is read as the file `name.cpp`.
- The NOT CHECKED section and the pnpm dependency rule are removed.
- Yarn 4 built-in commands (`yarn npm`, `yarn dlx`, `yarn workspaces`...) are no longer treated as scripts.
- The review sees every package that defines a script, not just two.
- In a nested instruction file, a path that only matches inside another package is shown as "found only elsewhere".
- Bold folder names (`**examples/**`) are read.

Regression on the 216 older repos: all 151 known real problems are still flagged, with no crashes.
