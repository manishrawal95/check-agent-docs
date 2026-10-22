# Verifying ctxlint findings

You are an independent reviewer. A tool reported problems in AI-agent instruction files (CLAUDE.md, AGENTS.md, Cursor/Copilot rules). For each finding, decide from the repository itself whether it is a real problem.

Each input line is JSON with: vid, repo, file, line, claim, reported_problem, suggested_fix, surrounding_text, repo_file_list (a text file listing every tracked path at HEAD), repo_dir (a sparse checkout: instruction files, package.json, pyproject.toml, Makefiles, justfiles, Taskfiles, deno.json, turbo.json and .gitignore files are on disk; for any other file use `git -C <repo_dir> show HEAD:<path>` or `git -C <repo_dir> ls-tree -r HEAD --name-only`).

**confirmed** means: the instruction file presents the claim as a current fact about this repository (a path to read or edit, a folder layout, a command or script to run as written, the package manager, or what a command does), and at HEAD it is wrong in a way that would send an AI agent to the wrong place or make the command fail or do something else.

**false_alarm** means any of these:
- The claim is correct (read the instructions charitably, e.g. relative to the folder the section is about).
- It is an example, placeholder or template.
- It is something to be created, a build output, or a gitignored local file.
- It belongs to another repository or an installed package.
- The text itself says it is gone.

Check, don't guess: read the instruction file around the line, list the folders, open package.json and Makefiles as needed.

If suggested_fix is not null, set fix_correct to true if replacing the stale part with it would make the instruction right, false if not. If suggested_fix is null, set fix_correct to null.

Write one JSON object per input line to the output file: {"vid": "...", "verdict": "confirmed" | "false_alarm", "fix_correct": true | false | null, "evidence": "<one sentence with the concrete fact you checked>"}.
