# Build and verification

Run `python3 build.py` from the repository root for the interactive menu. For reproducible validation, use:

```sh
python3 -m unittest discover -s tests -v
python3 build.py --all --prepare
python3 build.py --all
```

The first two commands need only Python. The last needs a working ConTeXt LMTX installation; use `--context /full/path/to/context` if necessary. The root `main.ctx` is compiled from each isolated `.build/<target>/` directory, not from the source root.

Check `selection.json`, `PathList.ctx` and `compile.log` for every target. The staged `project.json` identifies the project root for the font loader. Confirm that selected language, theme, page size and font files match the requested output, then inspect `outputs/advanced-<target>.pdf` with a PDF renderer.

Successful subprocess exit and unit tests are not proof of correct typesetting. Inspect line breaks, font weights, page layout and emoji. For Persian or mixed-direction content, follow `../fa/references/verification.md` and the Persian typography guide.

For host checks, discover registered projects and use the exact expected commit. A sandbox compilation or a simulated compiler test is not evidence that the Python script ran on the user's host. Report unavailable host capabilities explicitly; do not use another project's commands as a workaround.

## Recorded validation

On 2026-10-28, the interactive `build.py` prepared the real project and its four
selected trees were compiled with ConTeXt `2026.07.29 11:46` through the isolated
MCP compiler. A temporary Lua transport restored the selected files and original
relative paths inside the sandbox before loading the unchanged staged `main.ctx`.
This also exercised the `project.json` marker used by the font loader; the
transport did not run the Python script on the host.

Both English outputs shipped 3 pages and both Persian outputs shipped 4 pages.
The returned log tails contained no missing-character, missing-font or root-marker
errors. PDF downloads were blocked with HTTP 403 / Cloudflare code 1010 and the
cloud browser could not open the download, so these runs were not visually
verified. Do not claim that their glyph shaping or layout was inspected.

The local regression suite additionally exercises the interactive menu, real
script invocation using a simulated compiler, and preservation of an earlier PDF
when a subsequent compilation fails. Simulated output is never a typesetting test.
