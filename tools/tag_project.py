"""Tag resolution shared by the path generator, compiler and watcher (stdlib)."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKEN = re.compile(r'[a-z0-9][a-z0-9_]*\Z')


def validate_tags(tags, catalog):
    categories = set()
    for tag in tags:
        if tag not in catalog:
            raise ValueError(f'Unknown tag: {tag}')
        if catalog[tag] in categories:
            raise ValueError(f'Multiple tags from category {catalog[tag]}')
        categories.add(catalog[tag])


def load_config(root):
    config = json.loads((root / 'project.json').read_text(encoding='utf-8'))
    catalog = {}
    for category, tags in config['tag_categories'].items():
        if not tags or not isinstance(tags, list):
            raise ValueError(f'Invalid tag category: {category}')
        for tag in tags:
            if not isinstance(tag, str) or not TOKEN.fullmatch(tag) or tag in catalog:
                raise ValueError(f'Invalid or duplicate tag: {tag}')
            catalog[tag] = category
    if not TOKEN.fullmatch(config['project']):
        raise ValueError('project must be a simple lowercase identifier')
    components = config.setdefault('components', ['section', 'setups', 'sources'])
    if (
        not isinstance(components, list) or not components
        or any(not isinstance(name, str) or not TOKEN.fullmatch(name) for name in components)
        or len(set(components)) != len(components)
        or any(name in catalog for name in components)
    ):
        raise ValueError('components must contain unique folder names distinct from tags')
    for name, tags in config['targets'].items():
        if not re.fullmatch(r'[a-z0-9][a-z0-9_-]*', name):
            raise ValueError(f'Invalid target name: {name}')
        validate_tags(tags, catalog)
    return config, catalog


def logical_path(path, catalog):
    """Only tag-only subdirectories add conditions; filenames stay unchanged."""
    parts, tags = [], set()
    for i, part in enumerate(path.parts):
        tokens = part.split('-')
        if 0 < i < len(path.parts) - 1 and all(token in catalog for token in tokens):
            tags.update(tokens)
        else:
            parts.append(part)
    validate_tags(sorted(tags), catalog)
    return Path(*parts), frozenset(tags)


def resolve(root, active, catalog, components=None):
    validate_tags(active, catalog)
    if components is None:
        components = load_config(root)[0]['components']
    # Do not silently ignore the old sibling-folder layout during migration.
    for folder in root.iterdir():
        for component in components:
            if folder.is_dir() and folder.name.startswith(component + '-'):
                suffix = folder.name[len(component) + 1:]
                if all(tag in catalog for tag in suffix.split('-')):
                    raise ValueError(
                        f'Move legacy folder {folder.name}/ to {component}/{suffix}/'
                    )
    candidates = {}
    for component in components:
        folder = root / component
        if folder.is_symlink():
            raise ValueError(f'Symlinks are not supported: {component}')
        if not folder.is_dir():
            continue
        for source in sorted(folder.rglob('*')):
            relative = source.relative_to(root)
            if any(p.startswith('.') or p in {'Backups', '__pycache__'} for p in relative.parts):
                continue
            if source.is_symlink() or any(p.is_symlink() for p in source.parents if p != root):
                raise ValueError(f'Symlinks are not supported: {relative}')
            if not source.is_file() or source.suffix.lower() in {'.log', '.tuc', '.tmp', '.pyc'} or source.name.endswith('~'):
                continue
            logical, condition = logical_path(relative, catalog)
            if condition <= set(active):
                candidates.setdefault(logical, []).append((condition, source))
    selected = {}
    for logical, versions in sorted(candidates.items()):
        rank = max(len(tags) for tags, _ in versions)
        winners = [source for tags, source in versions if len(tags) == rank]
        if len(winners) != 1:
            raise ValueError(f'Ambiguous {logical}: ' + ', '.join(str(p.relative_to(root)) for p in winners))
        selected[logical] = winners[0]
    if not (root / 'main.ctx').is_file():
        raise ValueError('Missing main.ctx')
    selected[Path('main.ctx')] = root / 'main.ctx'
    basenames = {}
    for logical in selected:
        # Text and font inputs use basenames. Detect collisions before TeX search.
        if logical.name in basenames and logical.suffix.lower() not in {'.md', '.txt', '.py'}:
            raise ValueError(f'Duplicate resource basename: {basenames[logical.name]} and {logical}')
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
    build = root / '.build'
    build.mkdir(exist_ok=True)
    destination = build / name
    with tempfile.TemporaryDirectory(prefix=f'{name}-', dir=build) as temporary:
        snapshot = Path(temporary)
        for logical, source in selected.items():
            target = snapshot / logical
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        (snapshot / 'Generate-Outputs.py').write_text('# Staged root marker\n')
        directories = sorted({'.', *(p.parent.as_posix() for p in selected)})
        paths = ''.join('\\usepath[{' + p + '}]\n' for p in directories)
        paths += '\\setupexternalfigures[directory={' + ','.join(directories) + '}]\n'
        (snapshot / 'PathList.ctx').write_text(paths, encoding='utf-8')
        manifest = {'tags': list(tags), 'files': {p.as_posix(): str(s.relative_to(root)) for p,s in selected.items()}}
        (snapshot / 'selection.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        if destination.exists():
            shutil.rmtree(destination)
        shutil.move(str(snapshot), destination)
    return destination


def compile_target(root, config, name, directory):
    log = directory / 'compile.log'
    with log.open('w', encoding='utf-8') as output:
        result = subprocess.run(['context', '--batchmode', 'main.ctx'], cwd=directory,
                                stdout=output, stderr=subprocess.STDOUT)
    pdf = directory / 'main.pdf'
    if result.returncode or not pdf.is_file():
        raise ValueError(f'Compilation failed: {name}; see {log}')
    outputs = root / 'Outputs'
    outputs.mkdir(exist_ok=True)
    final = outputs / f"{config['project']}-{name}.pdf"
    temporary = final.with_suffix('.pdf.tmp')
    shutil.copy2(pdf, temporary)
    temporary.replace(final)
    print(f'[DONE] {final}', flush=True)


def run_pass(root, args, previous, prepare_only=False):
    config, catalog = load_config(root)
    if args.tags is not None:
        tags = [x.strip() for x in args.tags.split(',') if x.strip()]
        validate_tags(tags, catalog)
        targets = [('custom-' + '-'.join(sorted(tags)) if tags else 'custom-shared', tags)]
    else:
        targets = [(name, config['targets'][name]) for name in (args.target or config['targets'])]
    errors = 0
    for name, tags in targets:
        current = None
        try:
            selected = resolve(root, tags, catalog, config['components'])
            current = (fingerprint(selected), tuple(sorted(tags)), config['project'])
            if args.list:
                print(name + ': ' + ', '.join(tags))
                for logical, source in sorted(selected.items()):
                    print(f'  {logical.as_posix()} <- {source.relative_to(root)}')
            elif previous.get(name) != current:
                directory = stage(root, name, tags, selected)
                print(f'[READY] {name}: {directory}', flush=True)
                if not prepare_only and not args.prepare:
                    compile_target(root, config, name, directory)
                previous[name] = current
        except (ValueError, OSError) as error:
            errors += 1
            message = str(error)
            if previous.get((name, 'error')) != message:
                print(f'[ERROR] {message}', flush=True)
                previous[(name, 'error')] = message
            # Failed compilation is retried when its inputs change.
            if current is not None:
                previous[name] = current
    return int(bool(errors))


def main(prepare_only=False):
    p = argparse.ArgumentParser(description='Select ConTeXt files by tags, prepare, compile or watch.')
    p.add_argument('--root', type=Path, default=ROOT)
    choice = p.add_mutually_exclusive_group()
    choice.add_argument('--target', action='append', help='Named target (repeatable); default: all targets')
    choice.add_argument('--tags', help='Ad hoc comma-separated tags, e.g. fa,screen,s4')
    p.add_argument('--watch', action='store_true', help='Rebuild affected targets when selected files change')
    p.add_argument('--interval', type=float, default=0.5)
    p.add_argument('--list', action='store_true', help='Print selected mappings without writing files')
    p.add_argument('--prepare', action='store_true', help='Prepare snapshots without compilation')
    args = p.parse_args()
    if args.interval <= 0:
        p.error('--interval must be positive')
    previous = {}
    try:
        while True:
            try:
                status = run_pass(args.root.resolve(), args, previous, prepare_only)
                if not args.watch or args.list:
                    return status
            except (ValueError, OSError, KeyError, TypeError) as error:
                if not args.watch:
                    p.exit(1, f'[ERROR] {error}\n')
                if previous.get('_error') != str(error):
                    print(f'[ERROR] {error}', flush=True)
                    previous['_error'] = str(error)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        return 0
