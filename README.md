# ConTeXt AdvancedKit

A ConTeXt LMTX template with explicit English and Persian content, shared settings, and local tag folders.

## Start here

Install **Python 3.10+** and **ConTeXt LMTX**, open a terminal in this repository, and run:

```sh
python3 build.py
```

The interactive menu lets you:

1. Build PDFs.
2. Build PDFs and watch for changes.
3. Prepare the selected project without compiling.
4. Inspect which source files will be used.

Choose one output or all four: `en-screen`, `en-printed`, `fa-screen`, and `fa-printed`. Finished PDFs go into **`outputs/`**. Build files and logs go into `.build/<target>/`.

No Python packages need to be installed. If ConTeXt is outside your `PATH`, start the same menu with its full executable path:

```sh
python3 build.py --context /path/to/context
```

To verify your ConTeXt installation independently, run `context --version`.

## Where to edit

| Location | What belongs here |
| --- | --- |
| `build.py` | The only build entry point: menu, file selection, paths, compilation, and watching |
| `main.ctx` | Shared document entry point and load order |
| `section/ContentLayout.ctx` | Shared chapter order |
| `section/en/`, `section/fa/` | English and Persian chapter content |
| `setups/` | Shared layout, cover, macros, and font fallback |
| `setups/en/`, `setups/fa/` | Language, direction, labels, aliases, and base fonts |
| `setups/en-printed/`, `setups/fa-printed/` | Language-specific print fonts |
| `setups/screen/`, `setups/printed/` | Screen and print colors |
| `setups/s4/`, `setups/a5/` | Paper-size settings |
| `sources/` | Fonts, figures, symbols, and bibliography resources |
| `sources/FontCollection/en/`, `sources/FontCollection/fa/` | Fonts for each language, with their licenses |
| `sources/FontCollection/Emoji_font/` | Shared emoji font |
| `skills/` | Shared guidance for AI contributors |
| `skills/en/`, `skills/fa/` | Language-specific AI guidance and supporting resources |
| `project.json` | Component folders, tag categories, and named outputs |
| `outputs/` | Generated PDFs; kept in the repository as an empty destination |
| `tests/` | Automated developer checks; not part of writing or building a document |

**Shared files live directly in the parent folder.** Only differences go into tag subfolders. There is no extra `common/` layer, and English is always explicitly `en`, never an implicit shared language.

For a shared chapter, create `section/chapter2.ctx`. For translations, create `section/en/chapter2.ctx` and `section/fa/chapter2.ctx`. Add `\input{chapter2.ctx}` to `section/ContentLayout.ctx` to include it in the document.

The former `tools/` module and the two `Generate-*.py` launchers have been merged into `build.py`. You do not need to choose between scripts.

## How tag folders work

Each component owns its conditions. For example, `section/fa/` controls Persian content and `setups/fa/` controls Persian settings. One folder's conditions do not leak into its neighbours.

| Physical source | Logical path used for compilation | Condition |
| --- | --- | --- |
| `section/intro.ctx` | `section/intro.ctx` | Shared |
| `section/en/intro.ctx` | `section/intro.ctx` | `en` |
| `section/fa/intro.ctx` | `section/intro.ctx` | `fa` |
| `setups/fa/FontsDef.ctx` | `setups/FontsDef.ctx` | `fa` |
| `setups/fa-printed/FontsDef.ctx` | `setups/FontsDef.ctx` | `fa` AND `printed` |
| `setups/a5/Size.ctx` | `setups/Size.ctx` | `a5` |
| `sources/Images/fa/map.svg` | `sources/Images/map.svg` | `fa` |

Only complete subdirectory names made from registered tags are conditions. Filenames stay literal: `intro-fa.ctx` does not mean "Persian intro". Use `fa/intro.ctx` instead.

All conditions must match. The matching version with the most distinct tags wins. A shared file is the fallback; it is not loaded again alongside the selected version. Equal highest priorities are an error. For example, if both `fa/intro.ctx` and `a5/intro.ctx` match, add `fa-a5/intro.ctx` to resolve the tie.

Nested conditions such as `setups/fa/printed/FontsDef.ctx` work too, but the sample uses `fa-printed/` to keep folders shallow. Do not create both forms for the same file: they have equal priority.

Tag categories and targets live in `project.json`. Select at most one tag from each category. The sample requires a language, theme, and paper size for a complete build. Sizes and themes are independent: Persian screen output on A5 is a valid custom choice.

To add a component such as `writing` or `template`, add its folder name to `components`. It then follows the same rules without changing Python code. Only registered components are staged for TeX. `skills/` contains contributor guidance and is deliberately not a TeX input component; agents read shared guidance first, then the selected language's guide.

## Commands for repeatable builds

Running without an action or output option opens the menu. These options bypass the menu for terminals, editors, or automation:

```sh
# Build every configured output.
python3 build.py --all

# Build one output, or several by repeating --target.
python3 build.py --target fa-screen
python3 build.py --target en-screen --target fa-screen

# Build and watch; Ctrl+C stops the watcher.
python3 build.py --target fa-printed --watch

# Prepare files and paths without a ConTeXt installation.
python3 build.py --target fa-screen --prepare

# Inspect the physical-to-logical selection without writing files.
python3 build.py --target fa-screen --list

# Choose independent language, theme, and size tags.
python3 build.py --tags fa,screen,a5

# Work on another project, or see every option.
python3 build.py --root /path/to/project
python3 build.py --help
```

For custom tags, the interactive menu also offers a **Custom tags** choice. `--target`, `--tags`, and `--all` are alternatives. `--interval 1` changes the watch interval to one second.

The prepared directory contains `main.ctx`, `project.json`, generated `PathList.ctx`, only the selected resources, and `selection.json` describing the source of every file. To compile it manually, enter `.build/<target>/` and run `context --nonstopmode --batchmode main.ctx`. Do not compile the root `main.ctx` directly or put every tag variant on TeX's search path.

The font loader identifies the prepared project using `project.json`; it does not depend on a removed launcher script.

## Outputs and watching

A normal build produces, for example:

- `outputs/advanced-fa-screen.pdf`
- `.build/fa-screen/compile.log`
- `.build/fa-screen/selection.json`

The watcher rebuilds only affected outputs. A change in Persian content does not rebuild English output; a shared change rebuilds every output using it. Adding, deleting, moving, and renaming variants are detected. Fixing an input after a failed build triggers another attempt. A failed build preserves the last successful PDF.

`outputs/.gitkeep` keeps the destination folder in Git. Its generated contents and `.build/` are ignored. Attach PDFs from `outputs/` to a **GitHub Release** when you want to distribute them; this is optional and is not done automatically.

## AI guidance and developer checks

`skills/SKILL.md` and its `references/` hold shared project guidance. `skills/fa/SKILL.md` and `skills/en/SKILL.md` hold language-specific guidance. Persian smoke-test scripts and sample assets belong under `skills/fa/`. These are repository instructions, not automatically installed personal ChatGPT skills.

`tests/` protects tag selection, language separation, watching, staging, and the interactive command. It is for maintainers; users can start directly with `python3 build.py`.

```sh
python3 -m unittest discover -s tests -v
```

Tests that use a simulated compiler verify the Python workflow only. A real build must also be compiled with ConTeXt, its log checked, and its PDF rendered to verify Persian shaping, mixed-direction text, and emoji.

## Migrating from previous versions

| Old location or command | Current location or command |
| --- | --- |
| `Generate-Outputs.py` | `python3 build.py` or `python3 build.py --all` |
| `Generate-LoadPath.py` | `python3 build.py --prepare` |
| `tools/tag_project.py` | `build.py` |
| `skills/context-persian/` | Shared material in `skills/`; Persian material in `skills/fa/` |
| `section-fa/preface.ctx` | `section/fa/preface.ctx` |
| English text directly in `section/` | `section/en/` |
| `setups/FontsDef-fa-printed.ctx` | `setups/fa-printed/FontsDef.ctx` |
| `setups/Size-a5.ctx` | `setups/a5/Size.ctx` |
| `Outputs/` | New builds go to `outputs/`; existing PDFs are not moved or deleted |

Legacy sibling folders such as `section-fa/` produce an actionable migration error. Tag suffixes in filenames are no longer conditions. `.build/` is generated and can be regenerated with the new script.

`sources/Images/diagram1.png` is not used by the sample chapters; it remains a text placeholder and must be replaced before use as an image. Bibliography files remain starter placeholders.

## License

Project code is MIT-licensed. Third-party fonts and other assets have their own licenses; preserve their notices when distributing them.
