#!/usr/bin/env python3
"""Build ConTeXt AdvancedKit: one interactive entry point, Python standard library only."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOKEN = re.compile(r"[a-z0-9][a-z0-9_]*\Z")


def validate_tags(tags, catalog):
    categories = set()
    for tag in tags:
        if tag not in catalog:
            raise ValueError(f"Unknown tag: {tag}")
        if catalog[tag] in categories:
            raise ValueError(f"Multiple tags from category {catalog[tag]}")
        categories.add(catalog[tag])


def load_config(root):
    config = json.loads((root / "project.json").read_text(encoding="utf-8"))
    catalog = {}
    for category, tags in config["tag_categories"].items():
        if not tags or not isinstance(tags, list):
            raise ValueError(f"Invalid tag category: {category}")
        for tag in tags:
            if not isinstance(tag, str) or not TOKEN.fullmatch(tag) or tag in catalog:
                raise ValueError(f"Invalid or duplicate tag: {tag}")
            catalog[tag] = category
    if not TOKEN.fullmatch(config["project"]):
        raise ValueError("project must be a simple lowercase identifier")
    components = config.setdefault("components", ["section", "setups", "sources"])
    if (
        not isinstance(components, list)
        or not components
        or any(
            not isinstance(name, str) or not TOKEN.fullmatch(name)
            for name in components
        )
        or len(set(components)) != len(components)
        or any(name in catalog for name in components)
    ):
        raise ValueError(
            "components must contain unique folder names distinct from tags"
        )
    for name, tags in config["targets"].items():
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", name):
            raise ValueError(f"Invalid target name: {name}")
        validate_tags(tags, catalog)
    return config, catalog


def logical_path(path, catalog):
    """Only tag-only subdirectories add conditions; filenames stay unchanged."""
    parts, tags = [], set()
    for i, part in enumerate(path.parts):
        tokens = part.split("-")
        if 0 < i < len(path.parts) - 1 and all(token in catalog for token in tokens):
            tags.update(tokens)
        else:
            parts.append(part)
    validate_tags(sorted(tags), catalog)
    return Path(*parts), frozenset(tags)


def resolve(root, active, catalog, components=None):
    validate_tags(active, catalog)
    if components is None:
        components = load_config(root)[0]["components"]
    # Do not silently ignore the old sibling-folder layout during migration.
    for folder in root.iterdir():
        for component in components:
            if folder.is_dir() and folder.name.startswith(component + "-"):
                suffix = folder.name[len(component) + 1 :]
                if all(tag in catalog for tag in suffix.split("-")):
                    raise ValueError(
                        f"Move legacy folder {folder.name}/ to {component}/{suffix}/"
                    )
    candidates = {}
    for component in components:
        folder = root / component
        if folder.is_symlink():
            raise ValueError(f"Symlinks are not supported: {component}")
        if not folder.is_dir():
            continue
        for source in sorted(folder.rglob("*")):
            relative = source.relative_to(root)
            if any(
                p.startswith(".") or p in {"Backups", "__pycache__"}
                for p in relative.parts
            ):
                continue
            if source.is_symlink() or any(
                p.is_symlink() for p in source.parents if p != root
            ):
                raise ValueError(f"Symlinks are not supported: {relative}")
            if (
                not source.is_file()
                or source.suffix.lower() in {".log", ".tuc", ".tmp", ".pyc"}
                or source.name.endswith("~")
            ):
                continue
            logical, condition = logical_path(relative, catalog)
            if condition <= set(active):
                candidates.setdefault(logical, []).append((condition, source))
    selected = {}
    for logical, versions in sorted(candidates.items()):
        rank = max(len(tags) for tags, _ in versions)
        winners = [source for tags, source in versions if len(tags) == rank]
        if len(winners) != 1:
            raise ValueError(
                f"Ambiguous {logical}: "
                + ", ".join(str(p.relative_to(root)) for p in winners)
            )
        selected[logical] = winners[0]
    if not (root / "main.ctx").is_file():
        raise ValueError("Missing main.ctx")
    selected[Path("main.ctx")] = root / "main.ctx"
    basenames = {}
    for logical in selected:
        # Text and font inputs use basenames. Detect collisions before TeX search.
        if logical.name in basenames and logical.suffix.lower() not in {
            ".md",
            ".txt",
            ".py",
        }:
            raise ValueError(
                f"Duplicate resource basename: {basenames[logical.name]} and {logical}"
            )
        basenames[logical.name] = logical
    return selected


def fingerprint(selected):
    digest = hashlib.sha256()
    for logical, source in sorted(selected.items()):
        digest.update(logical.as_posix().encode())
        digest.update(str(source).encode())
        digest.update(hashlib.sha256(source.read_bytes()).digest())
    return digest.hexdigest()


def stage(root, name, tags, selected):
    """Copy only resolved files into an isolated tree with their logical names."""
    build = root / ".build"
    build.mkdir(exist_ok=True)
    destination = build / name
    with tempfile.TemporaryDirectory(prefix=f"{name}-", dir=build) as temporary:
        snapshot = Path(temporary)
        for logical, source in selected.items():
            target = snapshot / logical
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        shutil.copy2(root / "project.json", snapshot / "project.json")
        directories = sorted({".", *(p.parent.as_posix() for p in selected)})
        paths = "".join("\\usepath[{" + p + "}]\n" for p in directories)
        paths += "\\setupexternalfigures[directory={" + ",".join(directories) + "}]\n"
        (snapshot / "PathList.ctx").write_text(paths, encoding="utf-8")
        manifest = {
            "tags": list(tags),
            "files": {
                p.as_posix(): str(s.relative_to(root)) for p, s in selected.items()
            },
        }
        (snapshot / "selection.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        if destination.exists():
            shutil.rmtree(destination)
        shutil.move(str(snapshot), destination)
    return destination


def compile_target(root, config, name, directory, context="context"):
    log = directory / "compile.log"
    with log.open("w", encoding="utf-8") as output:
        result = subprocess.run(
            [context, "--nonstopmode", "--batchmode", "main.ctx"],
            cwd=directory,
            check=False,
            stdin=subprocess.DEVNULL,
            stdout=output,
            stderr=subprocess.STDOUT,
        )
    pdf = directory / "main.pdf"
    if result.returncode or not pdf.is_file():
        raise ValueError(f"Compilation failed: {name}; see {log}")
    outputs = root / "outputs"
    outputs.mkdir(exist_ok=True)
    final = outputs / f"{config['project']}-{name}.pdf"
    temporary = final.with_suffix(".pdf.tmp")
    shutil.copy2(pdf, temporary)
    temporary.replace(final)
    print(f"[DONE] {final}", flush=True)


def run_pass(root, args, previous):
    config, catalog = load_config(root)
    if args.tags is not None:
        tags = [x.strip() for x in args.tags.split(",") if x.strip()]
        validate_tags(tags, catalog)
        targets = [
            ("custom-" + "-".join(sorted(tags)) if tags else "custom-shared", tags)
        ]
    else:
        targets = [
            (name, config["targets"][name])
            for name in (args.target or config["targets"])
        ]
    errors = 0
    for name, tags in targets:
        current = None
        try:
            selected = resolve(root, tags, catalog, config["components"])
            current = (fingerprint(selected), tuple(sorted(tags)), config["project"])
            if args.list:
                print(name + ": " + ", ".join(tags))
                for logical, source in sorted(selected.items()):
                    print(f"  {logical.as_posix()} <- {source.relative_to(root)}")
            elif previous.get(name) != current:
                directory = stage(root, name, tags, selected)
                print(f"[READY] {name}: {directory}", flush=True)
                if not args.prepare:
                    compile_target(
                        root,
                        config,
                        name,
                        directory,
                        getattr(args, "context", "context"),
                    )
                previous[name] = current
        except (ValueError, OSError) as error:
            errors += 1
            message = str(error)
            if previous.get((name, "error")) != message:
                print(f"[ERROR] {message}", flush=True)
                previous[(name, "error")] = message
            # Failed compilation is retried when its inputs change.
            if current is not None:
                previous[name] = current
    return int(bool(errors))


def choose(prompt, options, default=None):
    """Ask again after invalid input; EOF and Ctrl+C are handled by main."""
    while True:
        answer = input(prompt).strip().lower() or default
        if answer in options:
            return answer
        print("Please choose one of: " + ", ".join(options))


def interactive_options(root, args, config, catalog):
    print("\nConTeXt AdvancedKit")
    print(f"Project: {root}")
    print(
        "Shared files stay in each parent folder; en/ and fa/ hold language-specific files."
    )
    print("\n1. Build PDFs")
    print("2. Build PDFs and watch for changes")
    print("3. Prepare selected files without compiling")
    print("4. Inspect which files will be selected")
    print("0. Exit")
    action = choose("Action [1]: ", ["0", "1", "2", "3", "4"], "1")
    if action == "0":
        return False
    args.watch = action == "2"
    args.prepare = action == "3"
    args.list = action == "4"
    names = list(config["targets"])
    print("\nChoose an output:")
    for index, name in enumerate(names, 1):
        print(f"{index}. {name} ({', '.join(config['targets'][name])})")
    print("a. All configured outputs")
    print("c. Custom tags")
    print("0. Exit")
    options = ["0", "a", "c", *[str(i) for i in range(1, len(names) + 1)]]
    selection = choose("Output [a]: ", options, "a")
    if selection == "0":
        return False
    if selection == "c":
        print("Available tags:")
        for category, tags in config["tag_categories"].items():
            print(f"  {category}: {', '.join(tags)}")
        while True:
            value = input("Tags, separated by commas (example: fa,screen,a5): ").strip()
            tags = [tag.strip() for tag in value.split(",") if tag.strip()]
            try:
                if not tags:
                    raise ValueError("Choose at least one tag")
                validate_tags(tags, catalog)
            except ValueError as error:
                print(f"[ERROR] {error}")
                continue
            args.tags = ",".join(tags)
            break
    elif selection != "a":
        args.target = [names[int(selection) - 1]]
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Build ConTeXt AdvancedKit. Run without options for the interactive menu.",
        epilog="Examples: python3 build.py | python3 build.py --all | "
        "python3 build.py --target fa-screen --watch",
    )
    parser.add_argument(
        "--root", type=Path, default=ROOT, help="Project root (default: this script)"
    )
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument(
        "--target", action="append", help="Configured output; repeat to select several"
    )
    selection.add_argument("--tags", help="Custom tags, e.g. fa,screen,a5")
    selection.add_argument(
        "--all", action="store_true", help="Select all configured outputs"
    )
    action = parser.add_mutually_exclusive_group()
    action.add_argument(
        "--prepare",
        action="store_true",
        help="Prepare files and paths without compiling",
    )
    action.add_argument(
        "--list", action="store_true", help="Inspect selection without writing files"
    )
    parser.add_argument(
        "--watch", action="store_true", help="Rebuild affected outputs until Ctrl+C"
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=0.5,
        help="Watch interval in seconds (default: 0.5)",
    )
    parser.add_argument(
        "--context", default="context", help="ConTeXt executable name or full path"
    )
    args = parser.parse_args(argv)
    if not math.isfinite(args.interval) or args.interval <= 0:
        parser.error("--interval must be a positive finite number")
    if args.watch and args.list:
        parser.error("--watch cannot be combined with --list")
    root = args.root.resolve()
    try:
        config, catalog = load_config(root)
        explicit = (
            args.target is not None
            or args.tags is not None
            or args.all
            or args.prepare
            or args.list
            or args.watch
        )
        if not explicit and not interactive_options(root, args, config, catalog):
            return 0
        for target in args.target or []:
            if target not in config["targets"]:
                raise ValueError(
                    f"Unknown output {target!r}; choose: {', '.join(config['targets'])}"
                )
        if args.tags is not None:
            validate_tags(
                [tag.strip() for tag in args.tags.split(",") if tag.strip()], catalog
            )
        if not args.prepare and not args.list and shutil.which(args.context) is None:
            raise ValueError(
                f"ConTeXt executable {args.context!r} was not found. "
                "Install ConTeXt LMTX or pass --context /path/to/context. "
                "Use --prepare to prepare files without compiling."
            )
        if not args.list:
            print(f"PDF folder: {root / 'outputs'}")
            print(f"Build files and logs: {root / '.build'}")
        if args.watch:
            print("Watching selected files. Press Ctrl+C to stop.", flush=True)
        previous = {}
        while True:
            try:
                status = run_pass(root, args, previous)
                if not args.watch:
                    return status
            except (ValueError, OSError, KeyError, TypeError) as error:
                if not args.watch:
                    raise
                if previous.get("_error") != str(error):
                    print(f"[ERROR] {error}", flush=True)
                    previous["_error"] = str(error)
            time.sleep(args.interval)
    except EOFError:
        print(
            "\nNo interactive input. For automation run: python3 build.py --all",
            file=sys.stderr,
        )
        return 2
    except KeyboardInterrupt:
        print("\nStopped.")
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"[ERROR] {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
