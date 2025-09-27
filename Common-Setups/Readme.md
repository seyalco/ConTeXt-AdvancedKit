# Variable Definitions & File Structure

This project organizes variables by **page size**, **text direction**, **document language**, **colors**, and **fonts** to ensure clarity, maintainability, and easy localization.

---

## Folder Structure Overview

- **Common-Versions/**
  - **Page Size files** (e.g., `A5.ctx`, `S4.ctx`)
  - **Text Direction files** (`RTL.ctx`, `LTR.ctx`)

- **Colors**
  - `Theme-Printed.ctx` → Color definitions for printed documents
  - `Theme-Screen.ctx` → Color definitions for on-screen documents

- **Fonts**
  - `FontsDef.ctx` → Font definitions for use in `setups.ctx`
  - Located in subfolders that account for both **page size** and **language**, since fonts may depend on both.

- **Language Folders**
  - `Vars-Lang.ctx` → Language-specific variables.
  - `To-Language.ctx` → Translations for commands from `setups.ctx`.

---

## Variable Naming Convention

To improve readability and reduce ambiguity, variable names follow these prefixes:

1. **Page Size-Dependent Variables**
   - Prefix: `size:`
   - Defined in the corresponding page size file (e.g., `Size-A5-Vars.ctx`, `Size-S4-Vars.ctx`).

2. **Text Direction-Dependent Variables**
   - Prefix: `dir:`
   - Defined in the text direction file (`Dir-LTR-Vars.ctx`, `Dir-RTL-Vars.ctx`).

3. **Language-Dependent Variables**
   - Prefix: `lang:`
   - Defined in the language variable file (`Vars-Lang.ctx`).

4. **Color Variables**
   - Prefix: `Col` *(recommended but readability)*
   - Defined using `\definecolor`
   - Stored in:
     - `Theme-Printed.ctx` → Colors for printed output
     - `Theme-Screen.ctx` → Colors for screen output

5. **Font Variables**
   - Prefix: `Font` *(recommended for readability)*
   - Defined in `FontsDef.ctx`
   - Stored in specialized subfolders (dependent on both **page size** and **language**)

---

## Command Translation

- All commands in `setups.ctx` must have an equivalent translation in the corresponding `To-Language.ctx` inside the target language folder.
- Ensures proper localization for multilingual projects.
