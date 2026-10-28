---
name: context-english
description: Edit and verify English ConTeXt AdvancedKit content, left-to-right layout, English fonts and print or screen variants. Use when the selected document language is en or an English typesetting issue needs investigation.
---

# English ConTeXt workflow

Read `../SKILL.md` and `../references/repository-map.md` for shared rules first.

Keep English chapters in `section/en/`. Read `setups/en/Lang-Vars.ctx`, `setups/en/Direction.ctx` and `setups/en/To-Language.ctx` for language labels, left-to-right direction and aliases. These source paths are relative to the repository root.

Use `setups/en/FontsDef.ctx` for the base Alan Sans typeface and `setups/en-printed/FontsDef.ctx` for the Lora print override. Inspect `sources/FontCollection/FontFeatures.ctx` before changing font features. Resolve the exact files under `sources/FontCollection/en/`; do not depend on an unverified system alias. Preserve the shared emoji fallback in `setups/FallbacksDef.ctx`.

Keep colors and paper sizes in their own tag folders, not in English content. Keep code used by both languages in the shared parent rather than copying it into this guide or into English-only setup files.

Build with `python3 build.py --target en-screen` and `python3 build.py --target en-printed`. Inspect the logs and rendered PDFs for readable text, line breaks, weights, page dimensions and emoji. Use the Persian guide as well when a task includes Persian or mixed-direction text; do not reverse Unicode strings to change direction.
