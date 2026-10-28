---
name: context-advancedkit
description: Build, edit and troubleshoot ConTeXt AdvancedKit projects, component-local tag folders, shared layouts, language selection, resources and the interactive Python builder. Use for repository structure, output selection, build failures, fonts, figures or adapting this template.
---

# AdvancedKit shared workflow

Read `../AGENTS.md`. Treat `../README.md`, `../project.json` and the current source files as authoritative.

Read `references/repository-map.md` for component responsibilities and tag selection. Read `references/verification.md` for build and test procedures.

Read `fa/SKILL.md` for Persian or mixed-direction typography. Read `en/SKILL.md` for English typography. These folders select subject-specific guidance, not the language used to talk to the user.

Keep genuinely shared instructions and resources directly under `skills/`; keep language-specific instructions and fixtures under `fa/` or `en/`. Do not add a redundant wrapper folder around this shared guide.

Use `python3 build.py` for the interactive workflow. For repeatable builds use `--target`, `--all`, `--prepare`, `--list` or `--watch`. Keep the Python implementation in this single entry point; keep regression checks in `tests/`.

Preserve shared-parent/tag-subfolder selection, explicit English and Persian variants, conflict detection, and old-PDF preservation on build failure. Keep user content separate from typography. Keep third-party asset licenses with the assets.

Do not claim compilation or visual correctness from unit tests alone. Report the exact checkout and whether a build used a local engine, a registered host check, or an adapted sandbox package. Never execute unrelated host checks to bypass an unavailable project runner.

Keep generated PDFs in `outputs/` and intermediates in `.build/`, both ignored by Git. Never commit private download URLs, credentials or caches. Repository guides are not automatically installed personal skills.
