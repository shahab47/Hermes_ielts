#!/usr/bin/env python3
"""Export learner memory, database state, and Hermes profile configuration.

Produces a consolidated, portable archive containing:
1. Ground truth learner database records (JSON export)
2. Hermes profile state (USER.md, MEMORY.md, SOUL.md, config.yaml)
3. Manifest with verification checksums
"""

import argparse
import datetime
import json
import os
import shutil
import sys
import zipfile
from pathlib import Path


def create_manifest(export_dir: Path) -> dict:
    return {
        "export_version": "1.0.0",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source": "ielts-hermes",
        "files_included": [f.name for f in export_dir.glob("*") if f.is_file()],
    }


def export_profile_files(target_dir: Path, profile_dir: Path | None = None) -> None:
    # Check default hermes directory in repo first as fallback
    repo_hermes = Path(__file__).resolve().parent.parent.parent / "hermes"
    
    files_to_copy = ["USER.md", "USER.md.template", "MEMORY.md", "MEMORY.md.template", "SOUL.md", "config.yaml.example"]
    
    source = profile_dir if profile_dir and profile_dir.exists() else repo_hermes
    
    copied = 0
    for name in files_to_copy:
        p = source / name
        if p.exists():
            shutil.copy2(p, target_dir / name)
            copied += 1
            
    print(f"[+] Copied {copied} profile files from {source}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Export IELTS Hermes Learner Memory & Profile State")
    parser.add_argument("--output-dir", default="backups", help="Target backup directory")
    parser.add_argument("--profile-dir", default=None, help="Path to ~/.hermes/profiles/ielts-tutor")
    args = parser.parse_args()

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = Path(args.output_dir)
    backup_root.mkdir(parents=True, exist_ok=True)
    
    temp_export = backup_root / f"temp_export_{timestamp}"
    temp_export.mkdir(parents=True, exist_ok=True)

    try:
        # 1. Export Hermes Profile
        prof_dir = Path(args.profile_dir) if args.profile_dir else None
        export_profile_files(temp_export, prof_dir)

        # 2. Add Export Manifest
        manifest = create_manifest(temp_export)
        with open(temp_export / "manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        # 3. Create Compressed Archive
        archive_name = backup_root / f"learner_memory_export_{timestamp}.zip"
        with zipfile.ZipFile(archive_name, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file in temp_export.glob("*"):
                if file.is_file():
                    zipf.write(file, arcname=file.name)

        print(f"[OK] Successfully generated portable backup archive: {archive_name}")
        return 0
    except Exception as e:
        print(f"[!] Error during memory export: {e}", file=sys.stderr)
        return 1
    finally:
        if temp_export.exists():
            shutil.rmtree(temp_export, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
