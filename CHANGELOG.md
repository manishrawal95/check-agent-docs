# Changelog

## 0.5.3 (not yet measured on fresh repos)

### Claude Code plugin
- `/ctxlint:check` skill: emits review packets, lets the session (or the `instruction-reviewer` subagent) review them, then applies the answers through ctxlint's guard rails. No API key needed.
- PostToolUse hook: after Claude edits an instruction file, the local checks run on it, and anything that doesn't exist is shown to Claude.
- New CLI options for agent-driven review: `--only FILE`, `--answers FILE`, `--review-instructions`. `--emit-packets` now writes only files that need review, and with `--format json` it lists them.
- `--fix` also applies a review's suggested fix when stage 1 found exactly one file with that name and the review agrees.
- `CLAUDE.md` (how to work on ctxlint), `ROADMAP.md` (what to fix next, with evidence) and `eval/` (the measurement harness, prompts and data).

### Fixes from round 5
Fixes for false alarms and misses found in round 5 (`SCORECARD.md`).
- `extra_state.cpp/.h` is read as the file `extra_state.cpp`, not as a folder.
- Removed the "NOT CHECKED" list from the review request and the pnpm dependency-binary rule. Package names aren't command names (`@playwright/test` provides `playwright`), and both caused false reports.
- Yarn 4 built-in commands (`yarn npm audit`, `yarn dlx`, `yarn workspaces`, ...) are no longer treated as scripts.
- The review sees every package.json that defines a mentioned script, not just the first two.
- In an instruction file inside a package, a shorthand path that only exists inside a different package is shown to the review as "found only elsewhere" instead of "found".
- Bold folder names in lists (`**examples/**`) are checked.

## 0.5.2

- `mise` tasks (`mise run x`) are read from `mise.toml` and `mise-tasks/`, with their bodies shown to the review.
- Bare file and folder names that exist only in another folder are shown to the review separately. Names under a heading that names their folder ("**Parser** (`src/parser/`)") are resolved against that folder.
- The review prompt says more precisely when a description of a command counts as wrong.
- Files containing names found only elsewhere are now sent for review.
- History lookups in facts-only mode are cached and capped.

## 0.5.1

These fixes came from measuring 0.5.0 on 78 fresh repos (`SCORECARD.md`, round 4) and from a second bug hunt: an independent code review plus 2,000 fuzzed inputs.

### Security
- `--fix` wrote through a predictable temp file that could be a symlink to anywhere. It now uses a private temp file in the same folder and an atomic rename.
- An instruction file that was a symlink to a file outside the repo was read and its content sent to the review API. Only regular files inside the repo are read now.
- A review answer could steer `--fix` to rewrite text unrelated to any missing path. Fixes now need a missing fact with the same file name.
- `--changed` passed refs starting with `-` to git, where they act as options. These are now refused, with `--end-of-options` as a backstop.
- Instruction files are sent marked as untrusted content. Control characters are removed, and text imitating ctxlint's own markers is neutralised.

### Fixed
- One long Makefile line could make ctxlint run for 100 seconds (regex backtracking).
- Any unexpected error exited with 1, the same code as "issues found". It now exits 2 with "internal error".
- `--changed` missed files renamed in the branch.
- A lone `\r` line ending, inline ```` ``` ```` in prose, and code fences indented inside lists broke line tracking.
- Submodule checks were slow on repos with many submodules.
- The review cache key ignored the API URL, and corrupt cache entries were trusted.
- A model reply quoting a path that exists could still be reported as a problem.
- Bare folder names (`` `plugins/` ``) gitignored by a `.gitignore` next to the instruction file were reported as missing.
- Unreadable Taskfiles, `pyproject.toml`, `deno.json`, Makefiles and justfiles made every task look missing. They are now treated as unknown.
- Taskfile `includes:` and tasks at any indentation are read.

### Better findings
- Template files are skipped entirely: files in `template/`, `templates/`, `scaffold/`, `boilerplate/`, `starter/` folders, or containing `%%NAME%%` / cookiecutter markers. Their paths describe the projects they create.
- Repo-root paths written with a leading slash (`` `/src/lib/store.ts` ``) are now checked. Lines about URL routes are left out.
- `pnpm clean:deps` (shorthand with a colon) now counts as a script, not a possible binary.
- `.js` import paths for `.ts`/`.tsx` files count as found.
- Placeholders like `internal/vN/`, `example-N`, `turbo <command>`, Go identifiers (`pkg/errors.CodedError`) and extension lists (`.web.ts/.web.tsx`) are no longer read as paths or names.
- Facts-only mode reports a missing path only when its top folder exists here, the path is in git history, or a file with the same name exists elsewhere. Paths into other repos and libraries are no longer reported. On round 4 data, facts-only precision went from 38% to 89% (dev check).
- Files longer than 3,000 lines get facts-only findings with a warning instead of a huge review request.

### Added
- `--sarif-out FILE`, so SARIF can be written next to the normal output.

## 0.5.0

Found by a new 69-test suite, an independent code review (20 bugs, 19 reproduced) and a regression run on 216 real repos.

### Fixed
- `--fix` could replace a whole sentence when the review quoted one; it now changes only the stale path token, at word boundaries, on every line it appears.
- `--fix` turned CRLF line endings into LF, crashed on non-UTF-8 files, and could follow a symlink outside the repo.
- `.lstrip("./")` stripped characters, not a prefix: `.github/x` became `github/x`, so fixes into dot-folders silently failed.
- Fixed issues were still reported after `--fix`, and the exit code stayed 1.
- Running from a subfolder found nothing; ctxlint now uses the repo root.
- Non-ASCII file and folder names were skipped (git quoted them); all git output is now read with `-z`.
- Staged but uncommitted files were treated as missing; the index is now read, not just `HEAD`.
- A real folder named `gen`, `tmp`, `logs`, `cache` etc. made every path under it count as build output.
- The placeholder filter skipped real paths containing `todo`, `id`, `name`, `n`, or "here" (`sphere.py`).
- An exact root path lost to a different-case match under the instruction file's folder; folder-tree entries no longer fall back to the repo root at all.
- Folder-tree diagrams rooted at the repo's own name were dropped; trees whose root name matches several folders now use the nearest one.
- Paths through symlinked folders were reported as dead.
- `make -C dir build`, `make -j4 test`, `just --list` produced bogus "missing target" findings.
- `include Makefile.frontend` (and any `Makefile.*`) wasn't read.
- `cd docs && npm install` was checked against the root lockfile instead of `docs/`'s.
- Scripts were accepted if *any* package.json defined them; now the nearest package.json chain is used (with `--filter`/`--workspace` respected).
- turbo.json config keys (`pipeline`, `tasks`) were counted as npm scripts.
- `bun run script/build.ts` and placeholder script names (`npm run <script>`) were treated as scripts.
- A stale path repeated on several lines was only reported once.
- Line numbers drifted after a form feed or Unicode line separator.
- Four-backtick code fences containing ``` fences broke parsing.
- `.clinerules/` and `.windsurf/rules/` folders weren't read; `.claude/CLAUDE.md` is now checked relative to its parent folder.
- A non-dict `scripts` field in package.json crashed the run.
- GitHub annotations weren't escaped (`%`, newlines, `,`, `:`).
- API problems crashed the run with exit 1 (same as "issues found"): network errors, non-JSON responses, truncated replies, extra text around the JSON, wrong item types. Now: retries with backoff and `Retry-After`; a failed file falls back to facts-only findings with a warning; a rejected key or unknown model exits 2 with a clear message.
- The Action pasted inputs straight into a shell script and sent an empty model name when none was set.
- Reading a file missing from a sparse checkout could trigger a network fetch for every config file.
- `--emit-packets` file names could collide.

### Added
- What each mentioned command really runs (script bodies, make/just recipes, task definitions) is shown to the review, so it can catch "`make lint` runs mypy" when it doesn't.
- Task runners: `pyproject.toml` project scripts, poe, pdm, hatch, Taskfile (`task x`), `deno task`, `turbo`.
- `<!-- ctxlint-disable-next-line -->`, `<!-- ctxlint-disable-line -->`, `<!-- ctxlint-disable -->` / `<!-- ctxlint-enable -->`.
- `--changed REF` (PRs), `--estimate`, `--exclude`, `--jobs`, `--no-cache`, `--format sarif`.
- Review results cached by content hash; parallel requests.
- Exit code 2 for errors.
- `pyproject.toml` (installable `ctxlint` command), CI workflow, and the Action's `changed-only` and `sarif-file` inputs.
