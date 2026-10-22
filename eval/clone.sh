#!/bin/sh
# Usage: eval/clone.sh <repos_dir> <list>   (list lines: owner/repo or owner_repo)
# Blobless, depth-1 clones with a sparse checkout of instruction and config files (see prep.sh).
set -e
dest="$1"; list="$2"; here=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$dest"; cd "$dest"
grep -v '^\s*$' "$list" | while read -r r; do
  case "$r" in */*) slug="$r" ;; *) slug=$(echo "$r" | sed 's/_/\//') ;; esac
  d=$(echo "$slug" | tr / _)
  [ -d "$d" ] && continue
  timeout 300 git clone -q --depth 1 --filter=blob:none --no-checkout "https://github.com/$slug" "$d" >/dev/null 2>&1 \
    || { echo "CLONE-FAIL $slug"; rm -rf "$d"; continue; }
  sh "$here/prep.sh" "$d"
  git -C "$d" ls-tree -r HEAD --name-only > "$d.tree"
done
