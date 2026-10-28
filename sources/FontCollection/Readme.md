# Project fonts

The parent `FontCollection/` directory holds shared setup files and resources. Language-specific fonts belong under the corresponding tag folder.

| Path | Purpose |
| --- | --- |
| `FontFeatures.ctx`, `FontsLoader.ctx` | Shared font features and loader |
| `Emoji_font/` | Shared emoji font |
| `en/Alan_Sans/`, `en/Lora/` | English fonts |
| `fa/Vazirmatn/`, `fa/Parastoo/` | Persian fonts |

`build.py` stages only the selected fonts under `.build/<target>/sources/FontCollection/`. `FontsLoader.ctx` finds that prepared root through `project.json` and searches its font directories. Keep each family's license alongside its files.

Put shared font families in the parent folder and language-specific families in `en/` or `fa/`. Configure their use in the matching `setups/en/FontsDef.ctx`, `setups/fa/FontsDef.ctx`, or print override.

Font filenames must be unique in a selected output. Prefer an `m-` prefix and `file:<actual-filename>` references to reduce collisions with system fonts. Update all references when renaming a file.
