#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the Chrome theme release ZIP.

Packaged: manifest.json, README.md, LICENSE, logo/
Excluded : store-assets/ (separate store uploads), scripts/, .gitignore, .codebuddy/

The archive is written into the default output folder (the parent of this
project) as chill-wave-theme-<version>.zip, then verified: the manifest inside
the archive must parse, its version must match the README badge, and every file
it references must exist in the archive.
"""
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT.parent.parent          # default output folder: .../vibe coding/
NAME = "chill-wave-theme"

PACKAGED = ["manifest.json", "README.md", "LICENSE"]
PACKAGED_DIRS = ["logo"]
EXCLUDED = {".git", ".gitignore", ".codebuddy", "__pycache__", "store-assets", "scripts"}


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def collect():
    items = []
    for rel in PACKAGED:
        src = ROOT / rel
        assert src.exists(), f"missing required file: {rel}"
        items.append(src)
    for d in PACKAGED_DIRS:
        base = ROOT / d
        assert base.is_dir(), f"missing required directory: {d}"
        for f in sorted(base.rglob("*")):
            if f.is_file() and not any(p in EXCLUDED for p in f.parts):
                items.append(f)
    return items


def build_zip(target):
    items = collect()
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for src in items:
            z.write(src, src.relative_to(ROOT).as_posix())
    return items


def verify(target, version):
    with zipfile.ZipFile(target) as z:
        names = z.namelist()
        assert "manifest.json" in names, "manifest.json missing from archive root"
        leaked = [n for n in names if any(part in EXCLUDED for part in Path(n).parts)]
        assert not leaked, f"archive contains excluded paths: {leaked}"
        data = json.loads(z.read("manifest.json").decode("utf-8"))
        assert data["version"] == version, f"version mismatch in archive: {data['version']}"
        for icon in data.get("icons", {}).values():
            assert icon in names, f"manifest references missing file: {icon}"
        readme = z.read("README.md").decode("utf-8")
        assert f"version-{version}-" in readme, "README version badge is out of sync"
    assert target.exists() and target.stat().st_size > 0, "archive missing or empty"
    return len(names)


def main():
    version = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))["version"]
    target = OUT_DIR / f"{NAME}-{version}.zip"
    items = build_zip(target)
    count = verify(target, version)
    print(f"packed {len(items)} file(s) -> {count} entry(ies)")
    print(f"archive : {target}")
    print(f"size    : {target.stat().st_size} bytes")
    print(f"md5     : {md5(target)}")
    print(f"verify  : exists={target.exists()} size={target.stat().st_size}")


if __name__ == "__main__":
    main()