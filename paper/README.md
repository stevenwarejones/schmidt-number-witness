# Manuscript

`manuscript.md` is the canonical editable source. It is a **review draft**: unpublished, not
externally validated, with no author identity, journal status, historical priority or human
expert validation asserted.

## Build

Needs Pandoc, XeLaTeX and the DejaVu Serif/Sans/Mono fonts named in the YAML header.

```sh
bash paper/build.sh
```

It resolves paths relative to itself, stops on failure, and writes only
`build/paper/manuscript.pdf`. Inspect the rendered pages, not just extracted text — missing glyphs,
clipped vectors, split headings and overlapping equations do not show up in a text dump:

```sh
pdftoppm -r 110 -png build/paper/manuscript.pdf /tmp/manuscript-review
```

The PDF is generated into **`build/paper/`**, with every other generated file. It is not
tracked: one canonical PDF belongs on a release, not in the history of every source edit. CI
builds it and uploads it as an artifact. Keeping it out of `paper/` also matters for
`manifest.py verify-archive`, which has no Git-ignore rules and would otherwise report it as an
unlisted file in an extracted snapshot.

## Provenance

The draft was written by **ChatGPT (OpenAI), working as "Astra"**, as part of the review
recorded in `docs/review_2026-09-07_ai.md`, and is contributed here under the repository's
license. It has not been rewritten by Claude. It has
not been rewritten, only repointed: the verifier path it names was renamed after it was
written -- the old routing verifier became `proofs/verify_qutrit.py` -- and the pinned commit
is updated to the snapshot the paper actually describes.

Its scope statements are the repository's: the valid inequality on the partial-local hull is a
corollary of published M3322 inequalities plus positivity; the proposed contribution is the
sharp Schmidt-number-two bound and the explicit qutrit separation; novelty is unresolved. See
`docs/PRIOR_ART.md` and `VERIFY.md`.
