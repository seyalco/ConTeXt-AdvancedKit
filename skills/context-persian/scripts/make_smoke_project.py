#!/usr/bin/env python3
"""Create a portable Persian/emoji specimen without editing the source repository."""
import argparse
from pathlib import Path
import shutil
import struct
import zlib


def make_project(repo: Path, out: Path) -> None:
    source_files = {
        "mainfont.ttf": repo / "Common-Sources/FontCollection/Vazirmatn/m-Vazirmatn_wght.ttf",
        "emojifont.ttf": repo / "Common-Sources/FontCollection/Emoji_font/m-Twemoji.Mozilla.ttf",
        "Vazirmatn-OFL.txt": repo / "Common-Sources/FontCollection/Vazirmatn/OFL.txt",
        "ASSET-NOTICE.md": repo / "Common-Sources/Readme.md",
    }
    setup = Path(__file__).resolve().parents[1] / "assets/setup.ctx"
    for source in [*source_files.values(), setup]:
        if not source.is_file():
            raise ValueError(f"Required resource not found: {source}")
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise ValueError("Choose a new or empty output directory; existing files are never replaced.")
    out.mkdir(parents=True, exist_ok=True)
    for name, source in source_files.items():
        shutil.copyfile(source, out / name)
    shutil.copyfile(setup, out / "setup.tex")
    # The repository's diagram1.png is a text placeholder. Create a real PNG fixture.
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff)
    pixels = b"".join(b"\x00" + bytes([65, 120, 95]) * 64 for _ in range(32))
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 64, 32, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(pixels)) + chunk(b"IEND", b"")
    (out / "figure.png").write_bytes(png)
    (out / "main.tex").write_text(
        "\\environment[setup]\n\\starttext\n\\input content.tex\n\\stoptext\n", encoding="utf-8"
    )
    (out / "content.tex").write_text(
        "این متن فارسی با فونت وزیرمتن نوشته شده است.\n\n"
        "متن فارسی در کنار ConTeXt Lab و عدد ۱۲۳۴ باید درست دیده شود.\n\n"
        "ایموجی‌های رنگی: 😀 👋 🌍 🚀 ✨ 💡 ❤️\n\n"
        "\\placefigure[here]{یک تصویر همراه پروژه}{\\externalfigure[figure.png][width=.65\\textwidth]}\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        make_project(args.repo_root.resolve(), args.out.resolve())
    except (ValueError, OSError) as error:
        parser.exit(1, f"Error: {error}\n")
    print(f"Project ready: {args.out.resolve()}\nCompile inside that directory with: context main.tex")


if __name__ == "__main__":
    main()
