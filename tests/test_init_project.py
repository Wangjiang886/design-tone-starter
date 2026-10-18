"""Behavior checks use only disposable local directories; no external services."""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "init_project.py"
spec = importlib.util.spec_from_file_location("init_project", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class InitializeTests(unittest.TestCase):
    def setUp(self):
        scratch_root = os.environ.get("DESIGN_TONE_TEST_ROOT")
        self.scratch = tempfile.TemporaryDirectory(prefix="design-tone-test-", dir=scratch_root)
        self.addCleanup(self.scratch.cleanup)
        self.base = Path(self.scratch.name)
        self.root = self.base / "新手项目 空格"

    def test_unicode_project_starts_unapproved_with_empty_delivery(self):
        result = module.initialize(self.root, "我的第一个项目")
        self.assertTrue(result["ok"])
        for folder in ["00_核心分区", "01_素材库", "02_过滤库", "03_制作区", "04_最终方案", "05_成品"]:
            self.assertTrue((self.root / folder).is_dir())
        state = json.loads((self.root / "00_核心分区/进度.json").read_text(encoding="utf-8"))
        self.assertEqual(state["project_type"], "undecided")
        self.assertFalse(state["visual_approved"])
        self.assertIsNone(state["preview"]["url"])
        self.assertEqual(state["audio"]["status"], "not_requested")
        self.assertEqual(list((self.root / "05_成品").iterdir()), [])

    def test_reinitialization_preserves_every_existing_byte_and_progress(self):
        module.initialize(self.root, "项目一", "video")
        progress = self.root / "00_核心分区/进度.json"
        state = json.loads(progress.read_text(encoding="utf-8"))
        state["stage"] = "iterate"
        state["preview"]["url"] = "http://localhost:4123/preview"
        progress.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
        custom = self.root / "01_素材库/图片/用户原件.bin"
        custom.write_bytes(b"original\x00\xff")
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        result = module.initialize(self.root, "另一个传入名称", "web")
        after = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        self.assertEqual(result["created_files"], [])

    def test_partial_project_only_gets_missing_files(self):
        (self.root / "00_核心分区").mkdir(parents=True)
        brief = self.root / "00_核心分区/01_项目简报.md"
        brief.write_bytes(b"accepted user brief")
        result = module.initialize(self.root, "续作")
        self.assertEqual(brief.read_bytes(), b"accepted user brief")
        self.assertEqual(len(result["created_files"]), 5)

    def test_directory_conflict_fails_before_any_new_files(self):
        self.root.mkdir()
        conflict = self.root / "01_素材库"
        conflict.write_bytes(b"keep")
        with self.assertRaises(ValueError):
            module.initialize(self.root, "有冲突")
        self.assertEqual(list(self.root.iterdir()), [conflict])
        self.assertEqual(conflict.read_bytes(), b"keep")

    def test_planned_file_conflict_fails_before_creating_other_sections(self):
        conflict = self.root / "00_核心分区/进度.json"
        conflict.mkdir(parents=True)
        with self.assertRaises(ValueError):
            module.initialize(self.root, "有冲突")
        self.assertFalse((self.root / "01_素材库").exists())

    def test_root_file_is_not_replaced(self):
        self.root.write_bytes(b"not a directory")
        with self.assertRaises(ValueError):
            module.initialize(self.root, "失败")
        self.assertEqual(self.root.read_bytes(), b"not a directory")

    def test_linked_section_cannot_redirect_writes(self):
        self.root.mkdir()
        outside = self.base / "outside"
        outside.mkdir()
        linked = self.root / "00_核心分区"
        junction = False
        try:
            try:
                linked.symlink_to(outside, target_is_directory=True)
            except OSError:
                if os.name != "nt":
                    raise
                made = subprocess.run(
                    ["cmd", "/c", "mklink", "/J", str(linked), str(outside)],
                    capture_output=True, text=True,
                )
                if made.returncode:
                    self.skipTest("This host cannot create a symlink or junction")
                junction = True
            with self.assertRaises(ValueError):
                module.initialize(self.root, "链接冲突")
            self.assertEqual(list(outside.iterdir()), [])
            self.assertFalse((self.root / "01_素材库").exists())
        finally:
            if junction:
                os.rmdir(linked)
            elif linked.is_symlink():
                linked.unlink()

    def test_cli_failure_has_nonzero_status_and_json_error(self):
        result = subprocess.run(
            [sys.executable, "-X", "utf8", str(SCRIPT), "--root", str(self.root), "--name", "  "],
            capture_output=True, encoding="utf-8",
        )
        self.assertEqual(result.returncode, 2)
        self.assertFalse(json.loads(result.stderr)["ok"])
        self.assertFalse(self.root.exists())


if __name__ == "__main__":
    unittest.main()
