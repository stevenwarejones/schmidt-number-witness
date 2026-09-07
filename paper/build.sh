#!/usr/bin/env bash
set -euo pipefail
paper_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
pandoc --from=markdown+tex_math_single_backslash \
  "$paper_dir/manuscript.md" --pdf-engine=xelatex \
  -o "$paper_dir/manuscript.pdf"
