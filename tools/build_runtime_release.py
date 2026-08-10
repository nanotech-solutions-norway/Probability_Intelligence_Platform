#!/usr/bin/env python3
"""Build a deterministic, non-deploying PIP runtime release bundle."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import re
import tarfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOTS = (
    Path("services/pip_api"),
    Path("contracts/fea_pip_shadow_contract_v2.schema.json"),
)
EXCLUDED_NAMES = {"pip_config.local.php", ".env"}
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")


def _source_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for relative in SOURCE_ROOTS:
        candidate = root / relative
        if candidate.is_file():
            files.append(candidate)
        elif candidate.is_dir():
            files.extend(path for path in candidate.rglob("*") if path.is_file())
        else:
            raise FileNotFoundError(f"required release source is missing: {relative.as_posix()}")

    safe_files = []
    for path in sorted(files, key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root)
        if path.name in EXCLUDED_NAMES or any(part.startswith(".env") for part in relative.parts):
            continue
        safe_files.append(path)
    return safe_files


def build_release(root: Path, output_dir: Path, git_sha: str) -> tuple[Path, Path]:
    normalized_sha = git_sha.strip().lower()
    if not SHA_PATTERN.fullmatch(normalized_sha):
        raise ValueError("git_sha must be a full 40-character lowercase hexadecimal commit SHA")

    files = _source_files(root)
    if not files:
        raise ValueError("release source set is empty")

    output_dir.mkdir(parents=True, exist_ok=True)
    archive_path = output_dir / f"pip-runtime-{normalized_sha}.tar.gz"
    manifest_path = output_dir / f"pip-runtime-{normalized_sha}.manifest.json"

    tar_buffer = io.BytesIO()
    file_entries = []
    with tarfile.open(fileobj=tar_buffer, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for path in files:
            relative = path.relative_to(root).as_posix()
            content = path.read_bytes()
            info = tarfile.TarInfo(name=f"pip-runtime/{relative}")
            info.size = len(content)
            info.mode = 0o644
            info.mtime = 0
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            archive.addfile(info, io.BytesIO(content))
            file_entries.append(
                {
                    "path": relative,
                    "sha256": hashlib.sha256(content).hexdigest(),
                    "size": len(content),
                }
            )

    with archive_path.open("wb") as output:
        with gzip.GzipFile(filename="", mode="wb", fileobj=output, mtime=0, compresslevel=9) as compressed:
            compressed.write(tar_buffer.getvalue())

    archive_hash = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    manifest = {
        "format_version": 1,
        "source_repository": "nanotech-solutions-norway/Probability_Intelligence_Platform",
        "source_git_sha": normalized_sha,
        "archive": archive_path.name,
        "archive_sha256": archive_hash,
        "files": file_entries,
        "deployment_authorized": False,
        "execution_allowed": False,
        "recommendation_release_allowed": False,
        "bookmaker_execution_enabled": False,
        "real_money_betting_enabled": False,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return archive_path, manifest_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--git-sha", required=True, help="reviewed 40-character Git commit SHA")
    parser.add_argument("--output-dir", type=Path, default=Path("dist/runtime-release"))
    args = parser.parse_args()
    archive, manifest = build_release(ROOT, args.output_dir, args.git_sha)
    evidence = json.loads(manifest.read_text(encoding="utf-8"))
    print(f"source_git_sha={evidence['source_git_sha']}")
    print(f"archive_sha256={evidence['archive_sha256']}")
    print(f"file_count={len(evidence['files'])}")
    print("deployment_authorized=false")
    print("payload_included=false")
    print(f"archive={archive}")
    print(f"manifest={manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
