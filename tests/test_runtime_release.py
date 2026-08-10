import hashlib
import json
import tarfile
import tempfile
import unittest
from pathlib import Path

from tools.build_runtime_release import ROOT, build_release


class RuntimeReleaseTests(unittest.TestCase):
    def test_release_is_deterministic_and_secret_safe(self):
        git_sha = "1" * 40
        with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
            first_archive, first_manifest = build_release(ROOT, Path(first_dir), git_sha)
            second_archive, second_manifest = build_release(ROOT, Path(second_dir), git_sha)

            self.assertEqual(first_archive.read_bytes(), second_archive.read_bytes())
            self.assertEqual(first_manifest.read_bytes(), second_manifest.read_bytes())

            manifest = json.loads(first_manifest.read_text(encoding="utf-8"))
            self.assertEqual(manifest["source_git_sha"], git_sha)
            self.assertEqual(manifest["archive_sha256"], hashlib.sha256(first_archive.read_bytes()).hexdigest())
            self.assertFalse(manifest["deployment_authorized"])
            self.assertFalse(manifest["execution_allowed"])

            paths = [entry["path"] for entry in manifest["files"]]
            self.assertEqual(paths, sorted(paths))
            self.assertIn("services/pip_api/public/api/v1/pip/health.php", paths)
            self.assertIn("services/pip_api/public/api/v1/probability/football/fixture.php", paths)
            self.assertIn("contracts/fea_pip_shadow_contract_v2.schema.json", paths)
            self.assertFalse(any("local" in path or ".env" in path for path in paths))

            with tarfile.open(first_archive, "r:gz") as archive:
                members = archive.getmembers()
                self.assertTrue(all(member.mtime == 0 for member in members))
                self.assertTrue(all(member.uid == 0 and member.gid == 0 for member in members))

    def test_rejects_abbreviated_or_invalid_sha(self):
        with tempfile.TemporaryDirectory() as output_dir:
            with self.assertRaises(ValueError):
                build_release(ROOT, Path(output_dir), "deadbeef")


if __name__ == "__main__":
    unittest.main()
