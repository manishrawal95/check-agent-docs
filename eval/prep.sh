#!/bin/sh
d="$1"
cd "$d" || exit 0
git ls-tree -r HEAD | awk '$1=="120000"{sub(/^[^\t]*\t/,""); print "/"$0}' > ../"$d".links
git sparse-checkout init --no-cone >/dev/null 2>&1
{ printf '%s\n' '**/CLAUDE.md' '**/AGENTS.md' '**/GEMINI.md' '**/.cursorrules' '.windsurfrules' '.clinerules' '.clinerules/**' '.windsurf/rules/**' '.github/copilot-instructions.md' '.github/instructions/**' '**/.cursor/rules/**' '**/package.json' '**/pyproject.toml' '**/Makefile' '**/makefile' '**/GNUmakefile' '**/Makefile.*' '**/makefile.*' '**/*.mk' '**/justfile' '**/Justfile' '**/.justfile' '**/*.just' '**/Taskfile.yml' '**/Taskfile.yaml' '**/taskfile.yml' '**/taskfile.yaml' '**/deno.json' '**/deno.jsonc' 'turbo.json' 'turbo.jsonc' '**/mise.toml' '**/.mise.toml' '**/mise/config.toml' '**/.config/mise.toml' 'mise-tasks/**' '.mise-tasks/**' 'mise/tasks/**' '.mise/tasks/**' '.config/mise/tasks/**' '**/.gitignore' '!**/node_modules/**'; cat ../"$d".links; } > ../"$d".sparse
git sparse-checkout set --no-cone --stdin < ../"$d".sparse >/dev/null 2>&1
timeout 400 git checkout -q HEAD >/dev/null 2>&1 || echo "CHECKOUT-FAIL $d"
