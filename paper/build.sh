#!/usr/bin/env bash
set -euo pipefail
paper_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
out_dir="$(cd -- "$paper_dir/.." && pwd)/build/paper"
mkdir -p "$out_dir"
pandoc --from=markdown+tex_math_single_backslash \
  "$paper_dir/manuscript.md" --pdf-engine=xelatex \
  -o "$out_dir/manuscript.pdf"
echo "wrote build/paper/manuscript.pdf"
