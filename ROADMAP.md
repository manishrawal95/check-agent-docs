# What needs fixing (priority order)

Measured state, from `SCORECARD.md`:
- Stage 1 is fast (0.1 s per repo) and its suggested fixes are right about 19 times in 20.
- The review stage is unstable. Precision was 89% in round 4 and 71% in round 5, against a 90% bar.
- Recall was 19–57% of the wrong claims a careful reviewer finds.
- Facts-only mode was 57% in round 5.

Each item below says where the evidence is and how to tell when it's done. Finish an item, add tests, run the regression (`eval/README.md`), and keep claims about gains for after a fresh round.

## P0: the review stage

1. **Measure the in-session review (the plugin path) on a fresh round.**
   - In Claude Code the reviewer is the session model or the `instruction-reviewer` subagent (Sonnet), not Haiku.
   - Round 5 showed Haiku missing wrong command descriptions it had evidence for, and turning soft hints into false reports.
   - Done when: round 6 (fresh repos, bars written first) is run with the subagent as reviewer, and the numbers are in `SCORECARD.md`.
2. **Fewer judgement-call false alarms (8 of 17 in round 5).** Typical cases:
   - Shorthand ("docs/whatsnew").
   - "Files not to modify" lists.
   - Folders created at install.
   - Files the docs say are created later.
   - Paths under a heading.

   Try adding the 2–3 lines around each NOT FOUND item, and a required `"evidence"` field in each answer quoting the fact that proves it wrong. `review_issues` would then drop answers whose evidence doesn't name a NOT FOUND or FOUND ONLY ELSEWHERE item.
3. **Wrong descriptions of commands (6 misses in round 5, with the script body in the packet).**
   - Consider a separate, narrow second pass: for each `describes_command` line, ask "does the body do what the comment says?" with only that line and that body.
   - Done when: fresh-round behaviour recall is reported separately and goes up without precision going down.

## P1: stage 1 gaps (deterministic, testable)

4. **Package aliases in paths.** `@prefect/ui-v2/src/api/mocks` should map `@scope/name` to the folder whose package.json has that name, then check the rest (round 5, a003/a004).
5. **`yarn --cwd DIR x`, `npm --prefix DIR x`, `pnpm -C DIR x`.** Check the script against DIR's package.json (round 5, a013).
6. **Commands in prose.** "also run pnpm test:core:zod" outside backticks is missed (a034/a035). Extract `(npm|pnpm|yarn|bun) (run )?[\w:.-]+` from prose only when the line is clearly an instruction.
7. **Gradle and Maven tasks.** `./gradlew revApiCheck` (a006). Read `build.gradle(.kts)` task names, or mark them skipped. Nx `project.json`, Cargo aliases and `bb.edn` are also unread.
8. **Symlinked instruction files whose target isn't checked out in sparse clones** (zed's `AGENTS.md` → `.rules` read as empty). In `eval/prep.sh`, add symlink targets to the sparse set.
9. **Line-number references** (`flows.py:3084` pointing at unrelated code, a001/a002). This is probably out of scope for stage 1. At most, flag `file:line` references past the end of the file.

## P2: facts-only mode (no API key)

10. **Round 5: 21 of 37 real.** The filters added after round 4 were fitted to round 4 data. Remaining false alarm families:
    - Examples ("adjust paths to your app").
    - Route paths (`access-rules/new`).
    - Branch-name patterns (`ui-v2/feature-description`).
    - Lint rule names (`marimo/host-imports`).
    - Files to write into.
    - Turbo-managed blocks describing installed packages.

    Either keep only the highest-confidence kinds (moved files with a unique new location; missing scripts in the nearest package.json), or say plainly in the output that facts-only findings need checking.

## P3: product

11. **Installable from PyPI**, and a tagged GitHub release so `uses: owner/ctxlint@v0` works.
12. **`--changed` in the hook.** Today the hook checks a whole instruction file after any edit to it. Consider also running when code files are moved or deleted (PostToolUse on Bash `git mv`/`rm`), using `--changed HEAD`.
