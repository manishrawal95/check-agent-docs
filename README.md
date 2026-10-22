# check-agent-docs

Checks that your `CLAUDE.md`, `AGENTS.md` and other agent instruction files still match your code. When a file moves, a script is renamed or the package manager changes and the instructions don't follow, it tells you which line is wrong and where the thing went.

```
$ check-agent-docs
src/pydantic_clai2/AGENTS.md:315  [moved]  tests/menu_script.py
    The scripted menu runner lives at tests/clai2/menu_script.py, not at tests/menu_script.py.
    fix: tests/clai2/menu_script.py
AGENTS.md:43  [other]  make lint          # mypy type checking
    make lint runs ruff and its recipe says no type checker is configured; it is not a mypy run.

12 instruction file(s), 2 issue(s), 0.9s
```

It reads `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `.cursor/rules/`, `.cursorrules`, `.github/copilot-instructions.md`, `.github/instructions/`, `.windsurfrules`, `.windsurf/rules/` and `.clinerules` (file or folder) in one pass.

## Why

Agents follow these files literally. When code moves and the instructions don't, the agent goes looking for a folder that isn't there, runs a script that was renamed, or installs with the wrong package manager. In tests on 216 popular open-source repos with agent files, 54 (1 in 4) had at least one instruction that was wrong at the current commit.

## How it works

1. **Local checks (fast, no network, no AI).** Every path, file name, folder-tree diagram, script, task, `make`/`just` target and install command is checked against the repo with git: tracked and staged files, every `.gitignore`, submodules, symlinked folders, the nearest lockfile, `package.json`, `pyproject.toml` (project scripts, poe, pdm, hatch), Makefiles (including `Makefile.*`), justfiles, Taskfiles, `deno.json`, turbo and mise. This takes about 0.1 s per repo, and `--fix` rewrites moved paths in place.
2. **AI review (optional, experimental).** With `ANTHROPIC_API_KEY` set, a small model reads each flagged instruction file next to those facts, including what each mentioned command really runs, and reports only claims that would mislead an agent. It skips examples, placeholders, files you're told to create, other repos and gitignored paths. Files where every claim checked out are never sent, results are cached, and requests run in parallel. Read [How good is it?](#how-good-is-it) before relying on it.

## Use it in Claude Code (plugin)

```
/plugin marketplace add manishrawal95/check-agent-docs
/plugin install check-agent-docs@check-agent-docs-marketplace
```

- **`/check-agent-docs:check`** checks every instruction file. Use `--fix` to rewrite moved paths, `--changed origin/main` for a branch, or `--only CLAUDE.md` for one file. The review is done by Claude in your session, or by the bundled `instruction-reviewer` subagent, so no API key is needed. The tool still applies its guard rails to the answers.
- **Automatic check after edits:** when Claude edits an instruction file, a hook runs the local checks (about 0.1 s, no network) and tells Claude about any path, script or target that doesn't exist.

To try it from a local copy: `claude --plugin-dir ./check-agent-docs`.

## Install the CLI

A single Python file with no dependencies (Python 3.10+; 3.11+ for `pyproject.toml` tasks).

```bash
pipx install git+https://github.com/manishrawal95/check-agent-docs
# or copy check_agent_docs.py into your repo and run: python3 check_agent_docs.py
```

## Use

```bash
check-agent-docs                          # current repo (works from any subfolder)
check-agent-docs --no-llm                 # local checks only
check-agent-docs --fix                    # rewrite moved paths in place (only the stale path changes)
check-agent-docs --changed origin/main    # only files affected by your branch's changes
check-agent-docs --format json|github|sarif
check-agent-docs --estimate               # how much would be sent for review; sends nothing
check-agent-docs --emit-packets DIR       # write review inputs for any agent; then:
check-agent-docs --answers answers.jsonl  # apply that agent's answers through the same guard rails
check-agent-docs --exclude 'docs/legacy/**'
```

Exit codes: `0` no issues, `1` issues found, `2` the tool couldn't run (bad path, rejected API key, unknown model).

### Silencing a finding

```markdown
<!-- check-agent-docs-disable-next-line -->
Run `make legacy-target` on the old build box.

<!-- check-agent-docs-disable -->
...anything in here is ignored...
<!-- check-agent-docs-enable -->
```

### GitHub Action

```yaml
# .github/workflows/check-agent-docs.yml
name: check-agent-docs
on: [pull_request]
jobs:
  check-agent-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: manishrawal95/check-agent-docs@v0
        with:
          anthropic-api-key: ${{ secrets.ANTHROPIC_API_KEY }}   # optional
          # changed-only: "true"      # default: on PRs, only files the PR affects
          # fail-on-issues: "false"
          # sarif-file: check-agent-docs.sarif # then upload with github/codeql-action/upload-sarif
```

Findings show up as annotations on the PR. If the tool itself fails (exit 2), the step fails, so a broken setup never looks green.

## How good is it?

Each version was frozen and its pass bars were written before the test. Each test ran on public repos the tool had never seen, with independent reviewers as ground truth. Every number is in [`SCORECARD.md`](SCORECARD.md), failures included, and the method is in [`eval/README.md`](eval/README.md).

- **Local checks:** about 0.1 s per repo. Their suggested fixes were right 18 of 19 times in the latest round. Without the AI review, 57% of findings were real, so treat them as leads to check.
- **AI review, not yet reliable:**
  - Precision was 89% in round 4 and 71% in round 5, against a 90% bar.
  - It finds 20 to 57% of the wrong claims a careful human reviewer finds.
  - It rarely catches wrong descriptions of what a command does.

[`ROADMAP.md`](ROADMAP.md) lists what to fix next, with the evidence for each item.

## Limits

- Claims about behaviour are only checked for commands whose body the tool can read (npm/pnpm/yarn/bun scripts, make, just, poe/pdm/hatch, Taskfile names, deno). Counts and API behaviour aren't checked.
- Nx `project.json`, `bb.edn`, Gradle and Cargo aliases aren't read yet.
- It checks the committed and staged tree plus new untracked files.
- With local checks only, a path whose whole top folder was deleted is reported only if git history shows it was there. Shallow CI checkouts (`fetch-depth: 1`) have no history, so use `fetch-depth: 0` if you want those.
- Template files (scaffolds copied into other projects) are skipped.

## Related

[sync-agent-docs](https://github.com/manishrawal95/sync-agent-docs) works across many repos: it keeps infra facts (hosts, ports, domains) consistent between them. check-agent-docs checks one repo's agent files against that repo's code.

## Development

```bash
python3 -m unittest discover -s tests -v   # 106 tests, each builds a small real git repo
```

Earlier versions were called ctxlint. The files in `eval/` keep that name because they record what was measured.

## License

MIT
