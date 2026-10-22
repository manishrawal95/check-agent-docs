# Context linter, gate 1 pass bars (written before running on any repo)

Set 2026-10-22, before the checker was run on any repository.

**Question:** Do real repos have agent context files (CLAUDE.md, AGENTS.md, Cursor rules, Copilot instructions, GEMINI.md) that make checkable claims that are wrong, and can a deterministic checker find them without crying wolf?

**Sample:** public GitHub repos that contain at least one agent context file, cloned at their current default branch.

**What counts as a confirmed wrong claim:** the file tells an agent to use a path, script, command target or package manager that does not exist or does not match the repo at its current commit, and a manual check of the repo confirms it.

| # | Bar | Pass if |
|---|-----|---------|
| 1 | Share of repos with at least one confirmed wrong claim | at least 30% |
| 2 | Precision: share of the checker's flags confirmed correct by hand | at least 90% |
| 3 | Speed: median time to check one repo (excluding clone) | under 5 seconds |

Every flag is reviewed by hand. Recall (wrong claims the checker misses) is not measured in this gate.
