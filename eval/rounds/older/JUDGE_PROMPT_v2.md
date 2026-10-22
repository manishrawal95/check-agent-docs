# Judge prompt v2 (stage 2 of the linter)

Changed from v1 after round 1: a file that moved is a real problem (v1 wrongly let "a nested location the text clearly means" count as existing). Everything else is unchanged.

A fast checker found a place where an AI-agent instruction file (CLAUDE.md, AGENTS.md, Cursor/Copilot rules) mentions a path, command or package manager that it could not find in the repository. Decide whether this is a real mistake in the instructions that would mislead an AI agent working in this repo.

Answer `real` if the instruction presents the thing as existing or working in THIS repository right now (a file or folder to read or edit, a command to run, the tool to install dependencies with) and it is not at that path. This includes files that were moved or renamed: if the checker says "same name found at", or you find it elsewhere, it is still `real` (the instruction points to the wrong place) and you give the new location as `suggested_fix`.

Answer `ignore` if any of these apply:
- it is an example, placeholder, naming pattern or template
- the reader is told to create, write, generate or save it, or it is build output, a cache, or created at runtime
- it lives in another repository, an installed package, an upstream project, or a user's own project or machine
- the text itself says it was deleted, removed, is not used, or is ignored
- the path is gitignored or local-only (check the repo's .gitignore if present)
- it exists at exactly the path the text gives, once you account for letter case, a missing file extension, or the path being relative to the instruction file's own folder

You may look things up: the file list and repo folder paths are given with each flag.
