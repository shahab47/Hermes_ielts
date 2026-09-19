#!/usr/bin/env python3
"""Restore learner memory, database state, and Hermes profile configuration from an archive."""

import argparse
import json
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Restore IELTS Hermes Learner Memory & Profile State")
    parser.add_argument("--archive", required=True, help="Path to backup zip archive")
    parser.add_argument("--profile-dir", required=True, help="Target path to ~/.hermes/profiles/ielts-tutor")
    args = parser.parse_args()

    archive_path = Path(args.archive)
    if not archive_path.exists():
        print(f"[!] Archive not found: {archive_path}", file=sys.stderr)
        return 1

    profile_dir = Path(args.profile_dir)
    profile_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        try:
            with zipfile.ZipFile(archive_path, "r") as zipf:
                zipf.extractall(temp_path)

            manifest_path = temp_path / "manifest.json"
            if manifest_path.exists():
                with open(manifest_path, encoding="utf-8") as f:
                    manifest = json.load(f)
                print(f"[+] Found valid archive manifest created at: {manifest.get('created_at')}")

            # Restore profile files
            restored = 0
            for item in temp_path.glob("*"):
                if item.name == "manifest.json":
                    continue
                if item.is_file():
                    shutil.copy2(item, profile_dir / item.name)
                    restored += 1

            print(f"[OK] Successfully restored {restored} configuration and memory files to: {profile_dir}")
            return 0
        except Exception as e:
            print(f"[!] Failed to restore memory archive: {e}", file=sys.stderr)
            return 1


if __name__ == "__main__":
    sys.exit(main())
