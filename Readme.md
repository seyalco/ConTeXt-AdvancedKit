# ConTeXt Advanced Kit

A sophisticated project structure for managing complex, multi-lingual, and multi-format typesetting projects with ConTeXt LMTX.

> **Note:** This project is the evolutionary successor to the **[ConTeXt-StarterKit](https://github.com/seyalco/ConTeXt-StarterKit)**. While the StarterKit provides an excellent foundation for standard, single-output documents, the Advanced Kit is engineered to manage projects that require multiple outputs (e.g., different languages, layouts, or editions) from a single, unified source. It inherits the core principles of modularity and resource management from its predecessor and elevates them to a new level of power and flexibility.

## Project Goal

This project provides a robust framework for managing documents that need to be produced in multiple languages and various output sizes (e.g., for print, desktop, and mobile).

Imagine you need to design a document in both English and Persian, and for each language, you require different layouts optimized for printing, desktop viewing, and mobile screens. This kit is designed to handle exactly that scenario, keeping your project organized, maintainable, and free of redundancy.

## Quick Start

1. Clone the repository  
   `git clone https://github.com/user/ConTeXt-Advanced-Kit.git`

2. Run path generation  
   `python Generate-LoadPath.py`

3. Build all outputs  
   `python Generate-Outputs.py`

## Core Concept: Factoring

The architecture of this project might seem complex at first, especially with its nested folder structure. However, it's based on a simple and powerful principle borrowed from mathematics: **factoring**.

Just as you can factor out a common term in a mathematical equation to simplify it, this project structure factors out common files and configurations.

```
(A * X) + (A * Y)  =>  A * (X + Y)
```

In our project:
- Files and settings that are shared across different output versions are placed in higher-level "common" directories.
- As we move deeper into the directory structure, we introduce files specific to that particular version (e.g., a specific language or output size).
- Finally, we arrive at a unique `main.ctx` file that contains only the code specific to that one final output, inheriting everything else from its parent directories.

This approach, which can be described as **Path-based Inheritance** or **Cascading Configuration**, provides several key advantages:

1.  **No Redundancy**: Common files are never duplicated. You only write them once.
2.  **Clear Separation**: Each `main.ctx` is compiled in its own isolated environment. There's no risk of file paths or settings from one version interfering with another.
3.  **Simplified File Naming**: You don't need to create complex filenames like `main-en-print.ctx`. The unique path to each `main.ctx` defines its context, making the project clean and intuitive.

### The Problem with Centralized Architectures

In projects with numerous output variations, a centralized main.ctx often becomes a complex web of conditionals and modes (\doifelse, \setupmodes). While effective for simpler cases, this model’s maintainability diminishes as complexity grows. Debugging a specific output requires reproducing a precise state, and every change carries the risk of unintended side effects on other outputs, demanding extensive testing.

Our factored architecture sidesteps these challenges entirely. Each main.ctx is, by design, an isolated and self-contained compilation unit. To debug any version, you simply compile it directly from its directory. This guarantees a clean, predictable environment every time, making development and maintenance significantly more robust and straightforward.

---

## How It Works: The Python Scripts

This project includes two powerful Python scripts to automate the entire build process.

### 1. `Generate-LoadPath.py`: Automatic Path Management

This script is the magic that makes path-based inheritance work seamlessly.

*   **Primary Goal**: To find all relevant asset directories for each `main.ctx` file and generate a `PathList.ctx` file alongside it.
*   **Output File**: The `PathList.ctx` contains the necessary ConTeXt commands (`\usepath` and `\setupexternalfigures`) that tell the compiler where to look for files like fonts, images, and other project components.
*   **Path Discovery Logic**: The script intelligently discovers paths based on three rules:
    1.  All subdirectories within any `Common-*` folder along the path to the `main.ctx`.
    2.  All local subdirectories located next to the `main.ctx` file.
    3.  All parent directories leading up to the project root.
*   **Overall Function**: The script scans the entire project for `main.ctx` files and automatically creates or updates the corresponding `PathList.ctx` for each one. To use it, simply `\input PathList.ctx` at the beginning of your `main.ctx`.

### 2. `Generate-Outputs.py`: The Build & Automation Tool

This script acts as the project's build engine, automating the compilation of all document versions.

Here is a step-by-step breakdown of what it does:

1.  **Cleanup**: It starts by deleting the `Outputs/` directory if it exists and creating a fresh, empty one. This ensures that every build is clean and contains no leftover files from previous compilations.
2.  **Task Discovery**: It recursively scans the entire project to find every single `main.ctx` file, creating a list of all compilation tasks.
3.  **High-Speed Parallel Compilation**: This is the script's smartest feature. Instead of compiling files one by one, it uses **multiprocessing**. It detects the number of CPU cores on your machine and runs that many compilation jobs simultaneously. If you have an 8-core CPU, it will compile 8 `main.ctx` files at the same time, dramatically reducing the total build time.
4.  **Output Management & Organization**:
    *   For each successfully compiled `main.ctx`, a `main.pdf` is generated.
    *   The script then renames this PDF to a descriptive name based on its path (e.g., `ccontext-advanced-kit-En-Printed.pdf`), preventing name collisions.
    *   Finally, it copies all the renamed PDF files into the central `Outputs/` directory.

In short, this script transforms the tedious, manual process of compiling a large, multi-file ConTeXt project into a single, fast, automated command, delivering all final documents neatly organized in one place.

---

## Extending the Structure

The power of this factoring approach goes beyond just languages and sizes. You can easily extend it for other variations.

For example, what if you need a **Teacher's Edition** and a **Student's Edition** of a book, where the teacher's version contains answers and extra notes? You could use ConTeXt's conditional commands (`\doif...`) for this.

However, for more significant variations, you can simply add another layer to our directory structure. The project's dimension would change from `2 (languages) * 2 (sizes)` to `2 * 2 * 2 (editions)`.

The directory structure might then look like this:

```
├── Common-something
├── Outputs
├── Generate-Outputs.py
└── En
    ├── Common-something
   └── Printed
        ├── Common-something
        ├── Teacher
        │   └── main.ctx  # Teacher's Edition
        └── Student
            └── main.ctx  # Student's Edition
```

In this scenario, the `main.ctx` files are moved to the deepest level, where they have the fewest commonalities with other versions.

For the sake of simplicity, this "Teacher/Student" layer is not included in the base project. However, by following the logic of factoring common elements until you reach the most unique endpoint, you can easily adapt and extend the structure to fit any level of complexity.

### A Note on Debugging

Even if a `main.ctx` file is incomplete and only contains `\starttext \stoptext`, the `Generate-Outputs.py` script will not fail for it. It will produce a (mostly empty) PDF for that version, allowing you to see the progress of each part of your project in the `Outputs` folder.

