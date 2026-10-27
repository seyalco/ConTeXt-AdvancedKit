# Verification and troubleshooting

## Reproduce instead of guessing

1. Identify the exact entry point and working directory.
2. Check the actual font filenames and generated resource paths.
3. Generate a portable specimen with `scripts/make_smoke_project.py`.
4. Compile with the current ConTeXt LMTX engine, retaining the log and engine version.
5. Render the PDF and inspect connected Persian letters, mixed Latin text, number order, marks, emoji color/coverage, caption layout and font weights.
6. Apply the smallest setup change that addresses the demonstrated problem and recompile the same specimen.

The flat adaptation was checked with ConTeXt `2026.07.29 11:46` through the user's isolated LMTX MCP on 2026-10-27, using AdvancedKit's Vazirmatn and Twemoji font files. A representative emoji subset was used for the remote smoke test to reduce payload size. That test covered `😀 👋 🌍 🚀 ✨ 💡 ❤️`, not all font glyphs or sequences. The full kit's four output variants were not rebuilt as part of that reduced test.

## Common symptoms

| Symptom | Check first |
| --- | --- |
| Disconnected Persian letters | Applied feature set, `script=arab`, initial/medial/final forms, cursive positioning, selected font |
| Latin words or digits reversed in Persian prose | Bidi processing and method, not Unicode string reversal |
| Empty squares or missing characters | Font coverage, exact fallback font resolution, attached fallback, codepoint ranges |
| Emoji render without color | Actual font format, color features, whether fallback is attached and selected |
| Font exists locally but remote compile fails | Packaged files, exact basenames, stale cache/resolver paths, sandbox access |
| Images disappear after moving an output | Working directory and regenerated `PathList.ctx` |
| `unknown script mtx-context.lua` | Engine installation/tree/resolver setup before document syntax |
| A figure compiles but has the wrong caption/size | Exported source and template figure setup; do not rewrite unrelated prose |

The tracked `Common-Sources/Images/diagram1.png` is a text placeholder. Do not present it as a validated raster file; use the generator's real PNG specimen or supply a real image.

A zero exit status proves compilation, not visual correctness. A missing-character diagnostic can occur in an otherwise successful run. Avoid matching generic log words like `missing` in capability descriptions as proof of a missing-glyph event; inspect the actual diagnostic.

## MCP packaging

Read the connector's current limits; do not assume they are stable. The current tool accepts a complete source and base64 assets under plain filenames, and compiles offline. The compiler cannot read local home directories or fetch remote fonts/images for you.

For the smoke project, send `main.tex` as `source`; send `setup.tex`, `content.tex`, `mainfont.ttf`, `emojifont.ttf`, and `figure.png` under `assets`. Base64-encode actual bytes, not filesystem paths. Do not include the PDF as an input asset. Keep private download capabilities out of source control; renew links through the connector when necessary.

## Updating knowledge

Re-read live definitions when they change. Keep newly verified examples in the specimen or reference files and state the engine, font dependencies and tested range. Do not commit temporary PDF URLs, generated caches or user credentials into this skill.
