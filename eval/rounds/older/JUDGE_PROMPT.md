# Judge prompt (stage 2 of the linter)

A fast checker found a place where an AI-agent instruction file (CLAUDE.md, AGENTS.md, Cursor/Copilot rules) mentions a path, command or package manager that it could not find in the repository. Your job: decide whether this is a real mistake in the instructions that would mislead an AI agent working in this repo.

Answer `real` only if the instruction presents the thing as existing or working in THIS repository right now (a file or folder to read or edit, a command to run, the tool to install dependencies with) and it does not exist.

Answer `ignore` if any of these apply:
- it is an example, placeholder, naming pattern or template
- the reader is told to create, write, generate or save it, or it is build output, a cache, or created at runtime
- it lives in another repository, an installed package, an upstream project, or a user's own project or machine
- the text itself says it was deleted, removed, is not used, or is ignored
- the path is gitignored or local-only (check the repo's .gitignore if present)
- it actually exists (check the file list carefully: other letter case, other extension, nested location the text clearly means)

You may look things up: the file list and repo folder paths are given with each flag.

If `real`, and a file with the same name exists elsewhere in the repo, give that path as `suggested_fix`.
