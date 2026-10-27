# Resources and file layout

## Shared versus output-specific files

| Location | Responsibility |
| --- | --- |
| `Common-Setups/` | Shared layout and behavior |
| `Common-Setups/Common-Versions/` | Direction, theme and paper-size variants |
| `Common-Sources/` | Shared fonts, images, bibliography and graphical symbols |
| `Fa/Common-Sections/` | Persian author content shared by output variants |
| `En/Common-Sections/` | English author content shared by output variants |
| `Fa/Screen/`, `Fa/Printed/` | Output entry points and output-specific setup |
| `En/Screen/`, `En/Printed/` | English output entry points and setup |
| `Outputs/` | Collected generated PDFs |

Inspect the chosen `main.ctx` before moving imports. The entry point loads paths/fonts, feature/fallback/typeface definitions, language/theme/size/direction variables, shared setup and layout, and then author content. A shared change can affect several output variants: verify the requested variants rather than assuming every output inherits identically.

## Paths

`Generate-LoadPath.py` discovers shared `Common-*` directories, their subdirectories, local output directories, and parent directories; it writes a `PathList.ctx` beside each `main.ctx`. It excludes `Backups`. Generated paths use forward slashes and include `\usepath` plus `\setupexternalfigures` configuration.

`FontsLoader.ctx` locates the project root using `Generate-Outputs.py`, recursively gathers font directories, extends `OSFONTDIR`, and refreshes the resolver when supported. Preserve that root marker when copying a full AdvancedKit project. A reduced MCP specimen should instead use exact flat filenames, as the smoke-project script does.

After adding/moving resources, regenerate paths from the repository root and review the changed files:

```sh
python3 Generate-LoadPath.py
```

Compile an individual output from its own directory first. `Generate-Outputs.py` compiles all discovered entry points and recreates `Outputs/`; inspect that behavior and preserve any valuable existing output before requesting a bulk rebuild.

## Images and symbols

Store shared figures in `Common-Sources/Images/`. The inspected `diagram1.png` is a text placeholder, not a real PNG; validate actual resource bytes rather than trusting a file extension. The smoke-project script generates its own valid PNG. Resolve them through the selected output's generated path configuration. Keep captions and author references in content, and reusable figure styling in setup.

`Common-Sources/Symbols/SymbolMap.ctx` imports `set_symbol_vars.ctx` and `set_symbol_map.ctx`, then defines `\ms{...}` for in-text symbol placement. The actual scripts include `tex_safe_renamer.py`, `set_symbol_vars.py` and `set_symbol_map.py`; some prose uses plural or different casing. Check actual tracked filenames before executing a command. Renaming assets can break references, so inspect the script and resulting diff before treating it as a harmless rebuild.

## Bibliography and source resources

At the inspected baseline, `Common-Sources/Bibliography/Bibliography.ctx` and `refs.bib` are placeholders. Their presence is not evidence of a complete citation system. Implement and verify a ConTeXt publication dataset when a task needs formal bibliography styles. Do not import BibLaTeX or citekeys that the current project never defines.

ConTeXt Lab currently keeps per-book reference records and exports inline citations as footnotes. That is a separate initial implementation, not a claim of complete AdvancedKit bibliography integration.
