# Resources and file layout

Use `Readme.md` and `project.json` as the current project contract.

| Location | Responsibility |
| --- | --- |
| `main.ctx` | Single shared entry point |
| `section/ContentLayout.ctx` | Shared chapter order |
| `section/en/`, `section/fa/` | Explicit English and Persian author content |
| `setups/` | Shared typography, cover and layout files |
| `setups/en/`, `setups/fa/` | Language-specific direction, labels, aliases and base fonts |
| `setups/en-printed/`, `setups/fa-printed/` | Language plus print font overrides |
| `setups/screen/`, `setups/printed/` | Theme-specific colors |
| `setups/s4/`, `setups/a5/` | Paper sizes |
| `sources/FontCollection/en/`, `sources/FontCollection/fa/` | Language-specific font families and licenses |
| `sources/FontCollection/Emoji_font/` | Shared emoji font |
| `.build/<target>/` | Generated selected tree, PathList.ctx, logs and selection.json |
| `Outputs/` | Successfully compiled PDFs |

Each component owns its tag subdirectories. Untagged files in the parent are
shared; English is explicitly `en`, never an implicit shared language. Register
additional component roots such as `writing` or `template` in `components` in
`project.json`; the resolver and watcher apply the same rules to them.

Run `python3 Generate-LoadPath.py --target fa-screen` to prepare selected files,
then compile inside `.build/fa-screen/` or use `Generate-Outputs.py` directly.
Only complete subdirectory names consisting of registered tags are conditions:
`fa`, `a5`, `fa-printed`. Tags are inherited as AND conditions and omitted from
logical paths. Filenames and ordinary folder names are literal: `intro-fa.ctx`
is not an override. Most-specific matches win; equal highest ranks fail.
`setups/fa/printed/FontsDef.ctx` and `setups/fa-printed/FontsDef.ctx` have the same
condition; do not create both. Legacy sibling roots like `section-fa/` are rejected
with migration instructions. Never put every variant on TeX's search path.

`--list` prints effective selection without writing. `--watch` rebuilds only
outputs whose resolved sources/configuration change. The project tests cover
local tag conditions, explicit language separation, combined conditions,
custom components and the actual four target selections.

FontsLoader locates the staged root using `Generate-Outputs.py` and searches
`sources/FontCollection`. Staging supplies that marker and only fonts for the
selected language. Use exact physical font filenames for offline work. The
standalone smoke generator reads the physical `fa/Vazirmatn` directory and emits
flat filenames.

Shared figures are in `sources/Images/`. `diagram1.png` is a text placeholder,
not a validated image. The smoke generator supplies a real PNG. Language-specific
figures can live in `sources/Images/fa/` or `sources/Images/en/` and inherit the
same selection rules.

`sources/Symbols/SymbolMap.ctx` imports `set_symbol_vars.ctx` and
`set_symbol_map.ctx`, and defines `\ms{...}`. The actual scripts are
`tex_safe_renamer.py`, `set_symbol_vars.py` and `set_symbol_map.py`. Inspect
renaming diffs because changing asset names can break author references.

`sources/Bibliography/Bibliography.ctx` and `refs.bib` remain placeholders.
Their presence does not imply a complete citation system. Use ConTeXt publication
datasets, not BibLaTeX. ConTeXt Lab's reference records/export are separate;
this refactor does not add an automatic AdvancedKit importer to Lab.
