# ctxlint

**Your CLAUDE.md is lying to your agent.** ctxlint finds the claims in your AI-agent instruction files that no longer match your repo — and tells you where things went.

```
$ ctxlint
src/pydantic_clai2/AGENTS.md:315  [moved]  tests/menu_script.py
    The scripted menu runner lives at tests/clai2/menu_script.py, not at tests/menu_script.py.
    fix: tests/clai2/menu_script.py
AGENTS.md:43  [other]  make lint          # mypy type checking
    make lint runs ruff and its recipe says no type checker is configured; it is not a mypy run.

12 instruction file(s), 2 issue(s), 0.9s
```

It reads `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `.cursor/rules/`, `.cursorrules`, `.github/copilot-instructions.md`, `.github/instructions/`, `.windsurfrules`, `.windsurf/rules/` and `.clinerules` (file or folder) — every tool's file, in one pass.

## Why

Agents follow these files literally. When code moves and the instructions don't, the agent goes looking for a folder that isn't there, runs a script that was renamed, or installs with the wrong package manager. In tests on 216 popular open-source repos with agent files, at least 1 in 4 (54 repos) had an instruction that's wrong at the current commit — including bun, PostHog, airflow, vscode, pydantic-ai, langflow and two of Anthropic's own repos.

## How it works

1. **Facts (local, fast, no network).** Every path, file name, folder-tree diagram, script, task, `make`/`just` target and install command is checked against the repo with git: tracked and staged files, every `.gitignore`, submodules, symlinked folders, the nearest lockfile, `package.json`, `pyproject.toml` (project scripts, poe, pdm, hatch), Makefiles (including `Makefile.*`), justfiles, Taskfiles, `deno.json`, turbo and mise.
2. **Review (optional).** With `ANTHROPIC_API_KEY` set, a small model reads each whole instruction file next to those facts — including what each mentioned command really runs — and reports only claims that would mislead an agent. It skips examples, placeholders, files you're told to create, other repos and gitignored paths. Files where every claim checked out are never sent, results are cached, and requests run in parallel.

No key? You still get the high-confidence findings from stage 1.

## Use it in Claude Code (plugin)

```
/plugin install ctxlint --marketplace <owner>/ctxlint
```

On older Claude Code: `/plugin marketplace add <owner>/ctxlint`, then `/plugin install ctxlint@ctxlint-marketplace`.

- **`/ctxlint:check`** checks every instruction file. Use `--fix` to rewrite moved paths, `--changed origin/main` for a branch, or `--only CLAUDE.md` for one file. The review is done by Claude in your session, or by the bundled `instruction-reviewer` subagent, so no API key is needed. ctxlint still applies its guard rails to the answers.
- **Automatic check after edits:** when Claude edits an instruction file, a hook runs the local checks (about 0.1 s, no network) and tells Claude about any path, script or target that doesn't exist.

To try it from a local copy: `claude --plugin-dir ./ctxlint`.

## Install the CLI

ctxlint is a single Python file with no dependencies (Python 3.10+; 3.11+ for `pyproject.toml` tasks).

```bash
pipx install git+https://github.com/<you>/ctxlint   # or: pip install .   or just: python3 ctxlint.py
```

## Use

```bash
ctxlint                          # current repo (works from any subfolder)
ctxlint --fix                    # rewrite moved paths in place (only the stale path changes)
ctxlint --changed origin/main    # only files affected by your branch's changes
ctxlint --format json|github|sarif
ctxlint --estimate               # how much would be sent for review; sends nothing
ctxlint --no-llm                 # facts only
ctxlint --emit-packets DIR       # write review inputs for any agent; then:
ctxlint --answers answers.jsonl  # apply that agent's answers through ctxlint's guard rails
ctxlint --exclude 'docs/legacy/**'
```

Exit codes: `0` no issues, `1` issues found, `2` ctxlint couldn't run (bad path, rejected API key, unknown model).

### Silencing a finding

```markdown
<!-- ctxlint-disable-next-line -->
Run `make legacy-target` on the old build box.

<!-- ctxlint-disable -->
...anything in here is ignored...
<!-- ctxlint-enable -->
```

### GitHub Action

```yaml
# .github/workflows/ctxlint.yml
name: ctxlint
on: [pull_request]
jobs:
  ctxlint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: <you>/ctxlint@v0
        with:
          anthropic-api-key: ${{ secrets.ANTHROPIC_API_KEY }}   # optional
          # changed-only: "true"      # default: on PRs, only files the PR affects
          # fail-on-issues: "false"
          # sarif-file: ctxlint.sarif # then upload with github/codeql-action/upload-sarif
```

Findings show up as annotations on the PR. If ctxlint itself fails (exit 2), the step fails, so a broken setup never looks green.

## How good is it?

Every version is frozen and the pass bars are written before the test. The test runs on public repos ctxlint has never seen, with independent reviewers as ground truth. All the numbers are in `SCORECARD.md`, failures included.

- **Stage 1 (local checks) is solid:** it runs in about 0.1 s per repo. Its suggested fixes were right 18 of 19 times in the latest round.
- **The review stage is not yet reliable:**
  - Precision was 89% in round 4 and 71% in round 5, against a 90% bar.
  - It finds 20–57% of the wrong claims a careful human reviewer finds.
  - It rarely catches wrong descriptions of what a command does.
- **Facts-only mode (no API key):** 57% of findings were real in round 5.

Treat findings as leads to check, not verdicts.
## Limits

- Claims about behaviour are only checked for commands whose body ctxlint can read (npm/pnpm/yarn/bun scripts, make, just, poe/pdm/hatch, Taskfile names, deno). Counts and API behaviour aren't checked.
- Nx `project.json`, `bb.edn`, Gradle and Cargo aliases aren't read yet.
- It checks the committed and staged tree plus new untracked files.
- In facts-only mode, a path whose whole top folder was deleted is reported only if git history shows it was there. Shallow CI checkouts (`fetch-depth: 1`) have no history, so use `fetch-depth: 0` if you want those.
- Template files (scaffolds copied into other projects) are skipped.

## Development

```bash
python3 -m unittest discover -s tests -v   # 100 tests, each builds a small real git repo
```

## License

MIT
