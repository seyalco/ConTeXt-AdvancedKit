# Resources and file layout

Use the root `Readme.md` and `project.json` as the current project contract.

| Location | Responsibility |
| --- | --- |
| `main.ctx` | Single shared entry point |
| `section/` | Shared author content (English sample) |
| `section-fa/` | Persian overrides with the same logical filenames |
| `setups/` | Shared and tag-specific typography, cover and layout |
| `sources/` | Fonts, figures, bibliography and graphical symbols |
| `.build/<target>/` | Generated selected tree, PathList.ctx, logs and selection.json |
| `Outputs/` | Successfully compiled PDFs |

Run `python3 Generate-LoadPath.py --target fa-screen` to prepare selected files,
then compile from `.build/fa-screen/` or use `Generate-Outputs.py` directly.
Both scripts use `tools/tag_project.py`: registered suffix tags on folders and
files are inherited as AND conditions; the most specific match wins; equal
highest ranks fail. Untagged files are Shared fallback. Never add every variant
to TeX's search path. `--list` prints the effective selection without writing.
`--watch` rebuilds only outputs whose resolved sources/configuration change.

FontsLoader locates the staged root using `Generate-Outputs.py` and searches
`sources/FontCollection`. Staging supplies that marker. Use exact physical font
filenames for offline work. The standalone smoke generator uses flat filenames.

Shared figures are in `sources/Images/`. `diagram1.png` is a text placeholder,
not a validated image. The smoke generator supplies a real PNG.

`sources/Symbols/SymbolMap.ctx` imports `set_symbol_vars.ctx` and
`set_symbol_map.ctx`, and defines `\ms{...}`. The actual scripts are
`tex_safe_renamer.py`, `set_symbol_vars.py` and `set_symbol_map.py`. Inspect
renaming diffs because changing asset names can break author references.

`sources/Bibliography/Bibliography.ctx` and `refs.bib` remain placeholders.
Their presence does not imply a complete citation system. Use ConTeXt publication
datasets, not BibLaTeX. ConTeXt Lab's reference records/export are separate;
this refactor does not add an automatic AdvancedKit importer to Lab.
