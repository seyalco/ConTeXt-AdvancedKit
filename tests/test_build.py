import argparse
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from build import (
    ROOT,
    compile_target,
    fingerprint,
    load_config,
    resolve,
    run_pass,
    stage,
)


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.write("main.ctx", "\\starttext\\input{intro.ctx}\\stoptext")
        self.config = {
            "project": "book",
            "tag_categories": {
                "language": ["en", "fa"],
                "size": ["a5", "s4"],
                "edition": ["teacher"],
            },
            "targets": {"fa": ["fa", "a5"]},
        }
        self.write("project.json", json.dumps(self.config))
        _, self.catalog = load_config(self.root)

    def write(self, path, text):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def selected(self, tags=("fa", "a5")):
        return resolve(self.root, tags, self.catalog)

    def test_shared_fallback_folder_inheritance_and_asset_override(self):
        self.write("section/intro.ctx", "shared")
        self.write("section/fa/intro.ctx", "fa")
        self.write("section/fa/only.ctx", "only fa")
        self.write("sources/figure.svg", "shared figure")
        self.write("sources/fa/figure.svg", "fa figure")
        selected = self.selected()
        self.assertEqual(selected[Path("section/intro.ctx")].read_text(), "fa")
        self.assertEqual(selected[Path("sources/figure.svg")].read_text(), "fa figure")
        en = self.selected(["en"])
        self.assertEqual(en[Path("section/intro.ctx")].read_text(), "shared")
        self.assertNotIn(Path("section/only.ctx"), en)
        self.assertEqual(
            self.selected([])[Path("section/intro.ctx")].read_text(), "shared"
        )

    def test_and_and_custom_category(self):
        self.write("setups/Fonts.ctx", "shared")
        self.write("setups/fa/Fonts.ctx", "fa")
        self.write("setups/fa-a5/Fonts.ctx", "fa a5")
        self.write("setups/fa-a5-teacher/Fonts.ctx", "teacher")
        self.assertEqual(self.selected()[Path("setups/Fonts.ctx")].read_text(), "fa a5")
        self.assertEqual(
            self.selected(["fa", "a5", "teacher"])[
                Path("setups/Fonts.ctx")
            ].read_text(),
            "teacher",
        )

    def test_tie_is_error_and_combined_condition_resolves(self):
        self.write("section/fa/intro.ctx", "fa")
        self.write("section/a5/intro.ctx", "a5")
        with self.assertRaisesRegex(ValueError, "Ambiguous"):
            self.selected()
        self.write("section/fa-a5/intro.ctx", "both")
        self.assertEqual(self.selected()[Path("section/intro.ctx")].read_text(), "both")

    def test_conflicting_or_unknown_active_tags(self):
        for tags in [["fa", "en"], ["unknown"]]:
            with self.assertRaises(ValueError):
                self.selected(tags)

    def test_repeated_inherited_tag_does_not_increase_rank(self):
        self.write("section/fa/fa/intro.ctx", "fa twice")
        self.write("section/a5/intro.ctx", "a5")
        with self.assertRaisesRegex(ValueError, "Ambiguous"):
            self.selected()

    def test_stage_removes_stale_files_and_never_exposes_other_variants(self):
        self.write("section/intro.ctx", "shared")
        override = self.write("section/fa/intro.ctx", "fa")
        out = stage(self.root, "fa", ["fa"], self.selected())
        self.assertEqual((out / "section/intro.ctx").read_text(), "fa")
        self.assertFalse((out / "section/fa").exists())
        self.assertNotIn("section/fa", (out / "PathList.ctx").read_text())
        self.write(".build/fa/stale.ctx", "old")
        override.unlink()
        stage(self.root, "fa", ["fa"], self.selected())
        self.assertFalse((out / "stale.ctx").exists())
        self.assertEqual((out / "section/intro.ctx").read_text(), "shared")

    def test_fingerprint_tracks_effective_changes_and_rename_delete_add(self):
        shared = self.write("section/intro.ctx", "shared")
        fa = self.write("section/fa/intro.ctx", "fa")
        initial = fingerprint(self.selected())
        shared.write_text("unused changed")
        self.assertEqual(initial, fingerprint(self.selected()))
        fa.write_text("fa changed")
        self.assertNotEqual(initial, fingerprint(self.selected()))
        before = fingerprint(self.selected())
        fa.unlink()
        self.assertNotEqual(before, fingerprint(self.selected()))
        before = fingerprint(self.selected())
        self.write("section/fa/new.ctx", "new")
        self.assertNotEqual(before, fingerprint(self.selected()))

    def test_watch_pass_rebuilds_only_affected_targets(self):
        self.config["targets"]["en"] = ["en", "a5"]
        self.write("project.json", json.dumps(self.config))
        self.write("section/intro.ctx", "shared")
        fa = self.write("section/fa/intro.ctx", "fa")
        shared_layout = self.write("section/ContentLayout.ctx", "shared layout")
        args = argparse.Namespace(tags=None, target=None, list=False, prepare=False)
        state = {}
        with (
            patch("build.compile_target") as compiler,
            contextlib.redirect_stdout(io.StringIO()),
        ):
            run_pass(self.root, args, state)
            self.assertEqual(compiler.call_count, 2)
            run_pass(self.root, args, state)
            self.assertEqual(compiler.call_count, 2)
            fa.write_text("changed")
            run_pass(self.root, args, state)
            self.assertEqual(compiler.call_count, 3)
            self.assertEqual(compiler.call_args.args[2], "fa")
            shared_layout.write_text("changed for both languages")
            run_pass(self.root, args, state)
            self.assertEqual(compiler.call_count, 5)
            self.assertEqual(
                {call.args[2] for call in compiler.call_args_list[-2:]}, {"fa", "en"}
            )

    def test_failed_compile_preserves_existing_outputs_and_logs(self):
        self.write("section/intro.ctx", "shared")
        self.write("outputs/book-fa.pdf", "previous good pdf")
        directory = stage(self.root, "fa", ["fa"], self.selected())
        with patch("build.subprocess.run") as runner:
            runner.return_value.returncode = 1
            with self.assertRaisesRegex(ValueError, "Compilation failed"):
                compile_target(self.root, self.config, "fa", directory)
        self.assertEqual(
            (self.root / "outputs/book-fa.pdf").read_text(), "previous good pdf"
        )
        self.assertTrue((directory / "compile.log").exists())

    def test_duplicate_tex_basenames_fail(self):
        self.write("section/intro.ctx", "one")
        self.write("setups/intro.ctx", "two")
        with self.assertRaisesRegex(ValueError, "Duplicate resource basename"):
            self.selected()

    def test_explicit_languages_never_leak_into_each_other(self):
        self.write("section/ContentLayout.ctx", "shared layout")
        self.write("section/en/intro.ctx", "English")
        self.write("section/fa/intro.ctx", "فارسی")
        for language, content in [("en", "English"), ("fa", "فارسی")]:
            selected = self.selected([language])
            self.assertEqual(selected[Path("section/intro.ctx")].read_text(), content)
            self.assertEqual(
                selected[Path("section/ContentLayout.ctx")].read_text(), "shared layout"
            )
        self.assertNotIn(Path("section/intro.ctx"), self.selected([]))

    def test_nested_resource_owner_and_combined_folder(self):
        self.write("sources/Images/map.svg", "common")
        self.write("sources/Images/fa/map.svg", "fa")
        self.write("sources/Images/fa/a5/map.svg", "fa a5")
        self.assertEqual(
            self.selected()[Path("sources/Images/map.svg")].read_text(), "fa a5"
        )
        self.write("sources/Images/fa-a5/map.svg", "same rank")
        with self.assertRaisesRegex(ValueError, "Ambiguous"):
            self.selected()

    def test_filenames_and_ordinary_folder_names_are_not_tag_conditions(self):
        self.write("section/intro-fa.ctx", "literal filename")
        self.write("sources/notes-fa/figure.svg", "literal folder")
        selected = self.selected(["en"])
        self.assertIn(Path("section/intro-fa.ctx"), selected)
        self.assertIn(Path("sources/notes-fa/figure.svg"), selected)

    def test_components_are_configured_and_scoped(self):
        self.config["components"] = ["writing", "template"]
        self.write("project.json", json.dumps(self.config))
        self.write("writing/intro.ctx", "shared")
        self.write("writing/fa/intro.ctx", "fa writing")
        self.write("template/en/Fonts.ctx", "en fonts")
        self.write("template/fa/Fonts.ctx", "fa fonts")
        self.write("section/ignored.ctx", "outside configured components")
        selected = self.selected()
        self.assertEqual(selected[Path("writing/intro.ctx")].read_text(), "fa writing")
        self.assertEqual(selected[Path("template/Fonts.ctx")].read_text(), "fa fonts")
        self.assertNotIn(Path("section/ignored.ctx"), selected)

    def test_invalid_components_and_conflicting_folder_conditions(self):
        self.write("setups/fa-en/Fonts.ctx", "invalid")
        with self.assertRaisesRegex(ValueError, "Multiple tags"):
            self.selected()
        for components in [
            [],
            "section",
            ["section", "section"],
            ["fa"],
            ["../escape"],
        ]:
            self.config["components"] = components
            self.write("project.json", json.dumps(self.config))
            with self.assertRaisesRegex(ValueError, "components"):
                load_config(self.root)

    def test_legacy_sibling_folder_has_actionable_migration_error(self):
        self.write("section-fa/intro.ctx", "legacy")
        with self.assertRaisesRegex(ValueError, "section/fa/"):
            self.selected()

    def test_shipped_project_selects_language_theme_and_size_for_all_outputs(self):
        config, catalog = load_config(ROOT)
        for target, tags in config["targets"].items():
            with self.subTest(target=target):
                selected = resolve(ROOT, tags, catalog)
                language = "fa" if "fa" in tags else "en"
                theme = "printed" if "printed" in tags else "screen"
                size = "a5" if "a5" in tags else "s4"
                for name in ["preface", "section1", "conclusion"]:
                    self.assertEqual(
                        selected[Path(f"section/{name}.ctx")],
                        ROOT / f"section/{language}/{name}.ctx",
                    )
                for name in ["Lang-Vars", "Direction", "To-Language"]:
                    self.assertEqual(
                        selected[Path(f"setups/{name}.ctx")],
                        ROOT / f"setups/{language}/{name}.ctx",
                    )
                fonts = language + ("-printed" if theme == "printed" else "")
                self.assertEqual(
                    selected[Path("setups/FontsDef.ctx")],
                    ROOT / f"setups/{fonts}/FontsDef.ctx",
                )
                self.assertEqual(
                    selected[Path("setups/Theme.ctx")],
                    ROOT / f"setups/{theme}/Theme.ctx",
                )
                self.assertEqual(
                    selected[Path("setups/Size.ctx")], ROOT / f"setups/{size}/Size.ctx"
                )
                font_paths = [
                    source.relative_to(ROOT).as_posix()
                    for source in selected.values()
                    if source.suffix == ".ttf"
                ]
                other = "en" if language == "fa" else "fa"
                self.assertTrue(
                    any(f"FontCollection/{language}/" in path for path in font_paths)
                )
                self.assertFalse(
                    any(f"FontCollection/{other}/" in path for path in font_paths)
                )


class CommandTests(unittest.TestCase):
    def test_interactive_prepare_reprompts_and_selects_a_target(self):
        from build import main

        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            config = {
                "project": "demo",
                "tag_categories": {"language": ["en", "fa"]},
                "targets": {"fa": ["fa"], "en": ["en"]},
            }
            (root / "project.json").write_text(json.dumps(config))
            (root / "main.ctx").write_text(r"\starttext Demo\stoptext")
            with (
                patch("builtins.input", side_effect=["bad", "3", "bad", "1"]),
                contextlib.redirect_stdout(io.StringIO()) as output,
            ):
                self.assertEqual(main(["--root", folder]), 0)
            self.assertTrue((root / ".build/fa/main.ctx").exists())
            self.assertTrue((root / ".build/fa/project.json").exists())
            self.assertFalse((root / ".build/fa/Generate-Outputs.py").exists())
            self.assertFalse((root / ".build/en").exists())
            self.assertIn("Please choose", output.getvalue())

    def test_inspection_never_writes_or_requires_context(self):
        from build import main

        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "project.json").write_text(
                json.dumps(
                    {
                        "project": "demo",
                        "tag_categories": {"language": ["fa"]},
                        "targets": {"fa": ["fa"]},
                    }
                )
            )
            (root / "main.ctx").write_text(r"\starttext Demo\stoptext")
            with (
                patch("builtins.input", side_effect=["4", "a"]),
                patch("build.shutil.which") as engine,
                contextlib.redirect_stdout(io.StringIO()),
            ):
                self.assertEqual(main(["--root", folder]), 0)
            engine.assert_not_called()
            self.assertFalse((root / ".build").exists())
            self.assertFalse((root / "outputs").exists())

    def test_menu_exit_and_eof_are_not_implicit_builds(self):
        from build import main

        for answer, expected in [("0", 0), (EOFError, 2)]:
            with (
                patch(
                    "builtins.input",
                    side_effect=[answer] if isinstance(answer, str) else answer,
                ),
                contextlib.redirect_stdout(io.StringIO()),
                contextlib.redirect_stderr(io.StringIO()),
            ):
                self.assertEqual(main([]), expected)

    def test_missing_engine_and_unknown_target_are_actionable(self):
        from build import main

        with (
            patch("build.shutil.which", return_value=None),
            contextlib.redirect_stderr(io.StringIO()) as error,
        ):
            self.assertEqual(main(["--all"]), 1)
        self.assertIn("--context", error.getvalue())
        self.assertIn("--prepare", error.getvalue())
        with contextlib.redirect_stderr(io.StringIO()) as error:
            self.assertEqual(main(["--target", "not-a-target", "--prepare"]), 1)
        self.assertIn("Unknown output", error.getvalue())

    def test_interactive_script_builds_and_preserves_previous_pdf_on_failure(self):
        import os
        import subprocess
        import sys

        if os.name == "nt":
            self.skipTest("The test engine uses a POSIX executable shebang")
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "project.json").write_text(
                json.dumps(
                    {
                        "project": "demo",
                        "tag_categories": {"language": ["fa"]},
                        "targets": {"fa": ["fa"]},
                    }
                )
            )
            (root / "main.ctx").write_text(r"\starttext Demo\stoptext")
            engine = root / "test-context"
            engine.write_text(
                f'#!{sys.executable}\nfrom pathlib import Path\nPath("main.pdf").write_bytes(b"%PDF-simulated-engine")\nprint("simulated compiler")\n'
            )
            engine.chmod(0o755)
            command = [
                sys.executable,
                str(ROOT / "build.py"),
                "--root",
                folder,
                "--context",
                str(engine),
            ]
            result = subprocess.run(
                command,
                input="1\na\n",
                text=True,
                capture_output=True,
                cwd=root.parent,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            pdf = root / "outputs/demo-fa.pdf"
            self.assertEqual(pdf.read_bytes(), b"%PDF-simulated-engine")
            self.assertIn("[DONE]", result.stdout)
            engine.write_text(f"#!{sys.executable}\nraise SystemExit(1)\n")
            result = subprocess.run(
                command + ["--all"], text=True, capture_output=True, check=False
            )
            self.assertEqual(result.returncode, 1)
            self.assertEqual(pdf.read_bytes(), b"%PDF-simulated-engine")
            self.assertTrue((root / ".build/fa/compile.log").exists())


if __name__ == "__main__":
    unittest.main()
