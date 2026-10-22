# check-agent-docs: working on this repo

check-agent-docs checks AI-agent instruction files (CLAUDE.md, AGENTS.md, Cursor/Copilot/Windsurf/Cline rules) against the repo they live in. This repo is also a Claude Code plugin. Read `ROADMAP.md` for what to fix next and `SCORECARD.md` for every measurement so far, failures included.

## Layout

- `check_agent_docs.py`: the whole tool, one file, standard library only (Python 3.10+, 3.11+ for `tomllib`).
  - **Stage 1** (`Repo`, `Facts`, `extract`, `check`, `check_path`, `stage1_issues`): local, deterministic facts from git.
  - **Stage 2** (`packet`, `REVIEW_INSTRUCTIONS`, `review_issues`): a model reviews each flagged file. `review_issues` enforces the guard rails on its answers.
  - `apply_fixes` rewrites only the stale path token.
- `tests/test_check_agent_docs.py`: unittest. Each test builds a small real git repo. There is a fake API server for stage 2.
- Plugin files:
  - `.claude-plugin/plugin.json` and `marketplace.json`
  - `skills/check/SKILL.md` (the `/check-agent-docs:check` flow: emit packets → review in-session → `--answers`)
  - `agents/instruction-reviewer.md`
  - `hooks/hooks.json` and `hooks/post_edit.py` (local check after edits to instruction files)
- `action.yml`: the GitHub Action. `pyproject.toml`: the `check-agent-docs` console script.
- `eval/`: the measurement harness, prompts, repo lists and known-real problems. `eval/README.md` explains the protocol.

## Commands

```bash
python3 -m unittest discover -s tests          # all tests (~25 s); must pass before any commit
python3 check_agent_docs.py . --no-llm         # dogfood: this repo's own instruction files must stay clean
claude plugin validate .                       # plugin manifest, skill, agent and hook checks
```

## Rules for changes

1. **Every behaviour change gets a test** in `tests/test_check_agent_docs.py` that builds a repo showing the case.
2. **Precision before recall.** A false report costs users more than a miss: each false alarm teaches them to ignore the tool.
3. **Never let the review contradict a verified fact.** `review_issues` drops claims about paths that exist. Keep that, and extend it rather than loosening it.
4. **Bump `PROMPT_VERSION`** whenever `REVIEW_INSTRUCTIONS` or the packet format changes (it is part of the cache key). Bump `VERSION` in `check_agent_docs.py`, `pyproject.toml` and `.claude-plugin/plugin.json` together.
5. **No new dependencies.** It must stay a single file people can drop into CI.
6. **Don't claim an improvement without a fresh round.** Dev checks on already-seen repos have fooled us twice: round 4's 89% facts-only became 57% on round 5. See `eval/README.md`.
7. **Never post findings on other people's repos** (issues, PRs, comments) without the maintainer's explicit permission.

## Gotchas

- Use `strip_dot_slash()`, never `.lstrip("./")`: lstrip strips characters, so `.github` becomes `github`.
- Read git output with `-z`; non-ASCII names are quoted otherwise.
- Test clones are blobless and sparse. `repo.read(..., committed_fallback=True)` must not fetch blobs over the network, and history may be one commit deep.
- List packets with `os.walk`/`find`, never a shell glob: globs skip dot-files, and this lost 15 files in round 4.
