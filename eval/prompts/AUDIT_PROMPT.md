# Blind audit of AI-agent instruction files

You are auditing instruction files written for AI coding agents (CLAUDE.md, AGENTS.md, GEMINI.md, Cursor/Copilot/Windsurf/Cline rules). Your goal: find every claim that is **wrong at the repository's current HEAD** and that the repository itself can settle. You have not seen any tool's output and must not run any linter.

Each line of your input file is: `<repo_dir>\t<instruction file path relative to repo>\t<line count>`.

The repo_dir is a sparse checkout. On disk you will find:
- instruction files
- package.json, pyproject.toml
- Makefiles, justfiles, Taskfiles, mise.toml
- deno.json, turbo.json
- .gitignore files

`<repo_dir>.tree` lists every tracked path at HEAD. For any other file, use `git -C <repo_dir> show HEAD:<path>`; `git -C <repo_dir> ls-tree HEAD <dir>/` lists a folder. Do not modify anything.

**What counts (two types):**
- `existence`: a path, file, folder, folder-tree entry, npm/pnpm/yarn/bun script, make/just/task/mise/poe target, or package manager that the file presents as current in THIS repo and that does not exist or is not where the file says. This includes moved files and different letter case, and scripts run from a folder whose package.json lacks them.
- `behaviour`: a statement about what a command, script, target or config does (the tool it runs, what it covers, flags, defaults, destinations) that the repo's own files show is wrong.

**What doesn't count:**
- Examples, placeholders, templates, files to be created, and build output or gitignored local files.
- Things in other repos or installed packages.
- Opinions, style rules, and API behaviour you can't settle from the repo.
- Version numbers and counts.

Read each instruction file fully, relative to its own folder (a section about a subfolder is relative to that folder). Check every concrete claim; don't sample. Be strict about evidence: only report what you verified.

Output: one JSON object per wrong claim, appended to your output file as JSONL:
{"repo": "<repo folder name, e.g. PrefectHQ_prefect>", "file": "<instruction file path>", "line": <int>, "claim": "<short quote>", "problem": "<one sentence>", "evidence": "<the concrete fact you checked>", "confidence": "high|medium", "type": "existence|behaviour"}

Write the output file incrementally (after each repo) so work is not lost. When finished, reply with counts by type.
