#!/usr/bin/env python3
"""Automated data retention and privacy purge utility (Phase 20).

Supports:
1. Audio file TTL cleanup (pruning raw recordings older than N days).
2. Hermes profile memory reset (restoring blank USER.md / MEMORY.md templates).
"""

import argparse
import shutil
import sys
import time
from pathlib import Path


def cleanup_audio_assets(audio_dir: Path, max_age_days: int, dry_run: bool = False) -> int:
    if not audio_dir.exists():
        print(f"[*] Audio directory does not exist: {audio_dir} (nothing to prune)")
        return 0

    now = time.time()
    cutoff_seconds = max_age_days * 86400
    pruned_count = 0
    reclaimed_bytes = 0

    for file_path in audio_dir.glob("*"):
        if file_path.is_file():
            file_age = now - file_path.stat().st_mtime
            if file_age > cutoff_seconds:
                size = file_path.stat().st_size
                if not dry_run:
                    file_path.unlink()
                pruned_count += 1
                reclaimed_bytes += size

    action = "Would prune" if dry_run else "Pruned"
    print(f"[OK] {action} {pruned_count} audio files older than {max_age_days} days ({reclaimed_bytes / 1024:.1f} KB reclaimed)")
    return pruned_count


def reset_profile_memory(profile_dir: Path, templates_dir: Path, dry_run: bool = False) -> None:
    if not profile_dir.exists():
        print(f"[!] Profile directory not found: {profile_dir}", file=sys.stderr)
        return

    templates = {
        "USER.md.template": "USER.md",
        "MEMORY.md.template": "MEMORY.md",
    }

    for tmpl_name, target_name in templates.items():
        tmpl_file = templates_dir / tmpl_name
        target_file = profile_dir / target_name
        if tmpl_file.exists():
            if not dry_run:
                shutil.copy2(tmpl_file, target_file)
            print(f"[OK] {'Would reset' if dry_run else 'Reset'} {target_file.name} to clean template")
        else:
            print(f"[!] Template {tmpl_name} not found in {templates_dir}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description="IELTS Hermes Data Retention & Purge Utility")
    parser.add_argument("--cleanup-audio", action="store_true", help="Prune audio files older than max age")
    parser.add_argument("--days", type=int, default=14, help="Max retention days for audio (default: 14)")
    parser.add_argument("--audio-dir", default="audio_storage", help="Audio storage directory")
    parser.add_argument("--reset-profile", action="store_true", help="Reset profile memory to templates")
    parser.add_argument("--profile-dir", default=None, help="Path to profile directory")
    parser.add_argument("--dry-run", action="store_true", help="Simulate actions without deleting")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent.parent
    templates_dir = repo_root / "hermes"

    if args.cleanup_audio:
        cleanup_audio_assets(Path(args.audio_dir), args.days, args.dry_run)

    if args.reset_profile:
        target_prof = Path(args.profile_dir) if args.profile_dir else repo_root / "hermes" / "profile" / "ielts-tutor"
        reset_profile_memory(target_prof, templates_dir, args.dry_run)

    if not args.cleanup_audio and not args.reset_profile:
        print("[*] No action specified. Use --cleanup-audio or --reset-profile. See --help.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
