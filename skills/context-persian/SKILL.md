---
name: context-persian
description: Create and troubleshoot Persian ConTeXt LMTX documents using AdvancedKit's font features, bidi settings, variable fonts, color emoji fallbacks, shared resources, and file layout. Use for Persian/English mixed text, missing glyphs, disconnected letters, font portability, figures, symbols, or adapting this template to ConTeXt Lab and isolated MCP compilation.
---

# Persian ConTeXt workflow

Read the current repository files before editing. Treat this skill as a workflow and map, not a replacement for the current setup. Keep author content separate from typography and file-resolution settings.

## Find the right layer

- Read `references/repository-map.md` before changing paths, shared content, output variants, bibliography, figures or symbols.
- Read `references/typography.md` before changing Persian shaping, bidi, variable weights, font lookup or emoji fallback.
- Read `references/verification.md` for a reproducible smoke project, MCP packaging and troubleshooting.
- Read `Common-Sources/FontCollection/FontFeatures.ctx`, the selected output's `FontsDef.ctx` and `FallbacksDef.ctx`, and `Common-Setups/Common-Versions/Dir-RTL-Vars.ctx` for the live definitions.

## Preserve these invariants

1. Keep Persian text in normal Unicode logical order. Preserve ZWNJ and punctuation. Never reverse strings to fix PDF direction.
2. Configure shaping, document language and bidi separately. `\mainlanguage[fa]` alone does not connect letters or correctly order embedded Latin text.
3. Use ConTeXt commands, not LaTeX packages such as `xepersian`, `fontspec` or `bidi`.
4. Resolve actual font files in the project. Do not assume a system font or a metadata alias exists in an offline compiler.
5. Keep emoji as Unicode author text and provide an explicit fallback font with the proper color features. Test sequences, not only isolated characters.
6. Keep setup/fonts/paths in template resources; keep chapters in content resources. Change the narrowest shared layer that affects the requested output.
7. Distinguish a compile exit status from a correct document. Inspect glyphs, punctuation, number order, embedded Latin text and emoji visually.
8. Preserve font/asset licensing when copying files; the repository's MIT license does not cover every third-party asset.

## Make and test a portable specimen

From the repository root:

```sh
python3 skills/context-persian/scripts/make_smoke_project.py --out /tmp/context-persian-smoke
cd /tmp/context-persian-smoke
context main.tex
```

Choose a new or empty output directory. The script copies the actual Vazirmatn and Twemoji files to stable local names, writes separate setup/content/main files, and includes a sample figure. It does not edit the repository's fonts, paths or outputs. It requires only Python's standard library; `context` is needed only for compilation.

For MCP, read the full emitted `main.tex` and provide the other generated `.tex`, image and font files as base64 assets with their exact plain filenames. Observe the connector's current size limits. Do not send absolute paths or assume the remote compiler can read your home directory.

## Maintain this skill

Add only tested or source-backed knowledge. Record the source paths and validation limits for new discoveries. Do not turn local font aliases, one engine version or a single successful emoji into a universal guarantee. Keep detailed examples in the reference files and runnable fixtures rather than expanding this entry point indefinitely.
