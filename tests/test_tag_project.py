import argparse
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.tag_project import load_config, resolve, fingerprint, stage, run_pass, compile_target


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.write('main.ctx', '\\starttext\\input{intro.ctx}\\stoptext')
        self.config = {'project': 'book', 'tag_categories': {'language': ['en', 'fa'], 'size': ['a5', 's4'], 'edition': ['teacher']}, 'targets': {'fa': ['fa', 'a5']}}
        self.write('project.json', json.dumps(self.config))
        _, self.catalog = load_config(self.root)

    def write(self, path, text):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding='utf-8')
        return p

    def selected(self, tags=('fa','a5')):
        return resolve(self.root, tags, self.catalog)

    def test_shared_fallback_folder_inheritance_and_asset_override(self):
        self.write('section/intro.ctx', 'shared')
        self.write('section-fa/intro.ctx', 'fa')
        self.write('section-fa/only.ctx', 'only fa')
        self.write('sources/figure.svg', 'shared figure')
        self.write('sources-fa/figure.svg', 'fa figure')
        selected = self.selected()
        self.assertEqual(selected[Path('section/intro.ctx')].read_text(), 'fa')
        self.assertEqual(selected[Path('sources/figure.svg')].read_text(), 'fa figure')
        en = self.selected(['en'])
        self.assertEqual(en[Path('section/intro.ctx')].read_text(), 'shared')
        self.assertNotIn(Path('section/only.ctx'), en)
        self.assertEqual(self.selected([])[Path('section/intro.ctx')].read_text(), 'shared')

    def test_and_and_custom_category(self):
        self.write('setups/Fonts.ctx', 'shared')
        self.write('setups/Fonts-fa.ctx', 'fa')
        self.write('setups/Fonts-fa-a5.ctx', 'fa a5')
        self.write('setups/Fonts-fa-a5-teacher.ctx', 'teacher')
        self.assertEqual(self.selected()[Path('setups/Fonts.ctx')].read_text(), 'fa a5')
        self.assertEqual(self.selected(['fa','a5','teacher'])[Path('setups/Fonts.ctx')].read_text(), 'teacher')

    def test_tie_is_error_and_combined_condition_resolves(self):
        self.write('section-fa/intro.ctx', 'fa')
        self.write('section/intro-a5.ctx', 'a5')
        with self.assertRaisesRegex(ValueError, 'Ambiguous'):
            self.selected()
        self.write('section-fa/intro-a5.ctx', 'both')
        self.assertEqual(self.selected()[Path('section/intro.ctx')].read_text(), 'both')

    def test_conflicting_or_unknown_active_tags(self):
        for tags in [['fa','en'], ['unknown']]:
            with self.assertRaises(ValueError):
                self.selected(tags)

    def test_repeated_inherited_tag_does_not_increase_rank(self):
        self.write('section-fa/intro-fa.ctx', 'fa twice')
        self.write('section/intro-a5.ctx', 'a5')
        with self.assertRaisesRegex(ValueError, 'Ambiguous'):
            self.selected()

    def test_stage_removes_stale_files_and_never_exposes_other_variants(self):
        self.write('section/intro.ctx', 'shared')
        override = self.write('section-fa/intro.ctx', 'fa')
        out = stage(self.root, 'fa', ['fa'], self.selected())
        self.assertEqual((out/'section/intro.ctx').read_text(), 'fa')
        self.assertFalse((out/'section-fa').exists())
        self.assertNotIn('section-fa', (out/'PathList.ctx').read_text())
        self.write('.build/fa/stale.ctx', 'old')
        override.unlink()
        stage(self.root, 'fa', ['fa'], self.selected())
        self.assertFalse((out/'stale.ctx').exists())
        self.assertEqual((out/'section/intro.ctx').read_text(), 'shared')

    def test_fingerprint_tracks_effective_changes_and_rename_delete_add(self):
        shared = self.write('section/intro.ctx', 'shared')
        fa = self.write('section-fa/intro.ctx', 'fa')
        initial = fingerprint(self.selected())
        shared.write_text('unused changed')
        self.assertEqual(initial, fingerprint(self.selected()))
        fa.write_text('fa changed')
        self.assertNotEqual(initial, fingerprint(self.selected()))
        before = fingerprint(self.selected())
        fa.unlink()
        self.assertNotEqual(before, fingerprint(self.selected()))
        before = fingerprint(self.selected())
        self.write('section-fa/new.ctx', 'new')
        self.assertNotEqual(before, fingerprint(self.selected()))

    def test_watch_pass_rebuilds_only_affected_targets(self):
        self.config['targets']['en'] = ['en','a5']
        self.write('project.json', json.dumps(self.config))
        self.write('section/intro.ctx','shared')
        fa = self.write('section-fa/intro.ctx','fa')
        args = argparse.Namespace(tags=None,target=None,list=False,prepare=False)
        state = {}
        with patch('tools.tag_project.compile_target') as compiler, contextlib.redirect_stdout(io.StringIO()):
            run_pass(self.root,args,state)
            self.assertEqual(compiler.call_count,2)
            run_pass(self.root,args,state)
            self.assertEqual(compiler.call_count,2)
            fa.write_text('changed')
            run_pass(self.root,args,state)
            self.assertEqual(compiler.call_count,3)
            self.assertEqual(compiler.call_args.args[2],'fa')

    def test_failed_compile_preserves_existing_outputs_and_logs(self):
        self.write('section/intro.ctx','shared')
        self.write('Outputs/book-fa.pdf','previous good pdf')
        directory=stage(self.root,'fa',['fa'],self.selected())
        with patch('tools.tag_project.subprocess.run') as runner:
            runner.return_value.returncode=1
            with self.assertRaisesRegex(ValueError,'Compilation failed'):
                compile_target(self.root,self.config,'fa',directory)
        self.assertEqual((self.root/'Outputs/book-fa.pdf').read_text(),'previous good pdf')
        self.assertTrue((directory/'compile.log').exists())

    def test_duplicate_tex_basenames_fail(self):
        self.write('section/intro.ctx','one')
        self.write('setups/intro.ctx','two')
        with self.assertRaisesRegex(ValueError,'Duplicate resource basename'):
            self.selected()


if __name__ == '__main__':
    unittest.main()
