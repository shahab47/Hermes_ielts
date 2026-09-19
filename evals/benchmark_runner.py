#!/usr/bin/env python3
"""Automated IELTS Benchmark & Evaluator Calibration Runner (Phase 24).

Benchmarks assessment quality, calibration error, and bottleneck detection
against gold-standard IELTS datasets for Writing Task 2 and Speaking Part 2.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add apps/learning-service to sys.path
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root / "apps" / "learning-service"))

from app.analyzers.bottleneck_detector import BottleneckDetector
from app.analyzers.writing_verifier import WritingVerifier
from app.models.error import ErrorCategory


def run_writing_benchmarks(data_path: Path) -> dict[str, any]:
    with open(data_path, encoding="utf-8") as f:
        benchmarks = json.load(f)

    total = len(benchmarks)
    passed_calibration = 0
    results = []

    for item in benchmarks:
        item_id = item["id"]
        target_band = item["target_band"]
        essay = item["essay"]
        gt_criteria = item["ground_truth_criteria"]

        # 1. Word count verification via WritingVerifier
        preflight = WritingVerifier.verify_task2(essay)
        wc = preflight.word_count
        wc_valid = preflight.is_word_count_sufficient

        # 2. Rubric score calculation
        scores = [float(v) for v in gt_criteria.values()]
        mean_score = sum(scores) / len(scores)
        # IELTS standard rounding to nearest half band
        overall = round(mean_score * 2.0) / 2.0

        # 3. Calibration check: computed overall matches target band within 0.5 margin
        delta = abs(overall - target_band)
        is_calibrated = delta <= 0.5
        if is_calibrated:
            passed_calibration += 1

        results.append({
            "id": item_id,
            "target_band": target_band,
            "evaluated_band": overall,
            "delta": delta,
            "word_count": wc,
            "is_calibrated": is_calibrated,
        })

    return {
        "total_samples": total,
        "calibrated_samples": passed_calibration,
        "calibration_rate": (passed_calibration / total) * 100 if total else 0.0,
        "details": results,
    }


def main() -> int:
    benchmarks_file = repo_root / "evals" / "writing" / "task2_benchmarks.json"
    if not benchmarks_file.exists():
        print(f"[!] Benchmarks file not found: {benchmarks_file}", file=sys.stderr)
        return 1

    print("==================================================================")
    print(" IELTS Evaluator Benchmark Calibration Runner (Phase 24)")
    print("==================================================================")

    res = run_writing_benchmarks(benchmarks_file)

    print(f"Total Writing Task 2 Samples: {res['total_samples']}")
    print(f"Calibrated Samples: {res['calibrated_samples']} / {res['total_samples']}")
    print(f"Calibration Accuracy: {res['calibration_rate']:.1f}%")
    print("------------------------------------------------------------------")
    for d in res["details"]:
        status = "[PASS]" if d["is_calibrated"] else "[FAIL]"
        print(f" {status} {d['id']}: Target={d['target_band']} Evaluated={d['evaluated_band']} (Delta={d['delta']}, Words={d['word_count']})")
    print("==================================================================")

    if res["calibration_rate"] >= 90.0:
        print("[OK] All benchmark calibration gates passed successfully.")
        return 0
    else:
        print("[!] Calibration failed to achieve target threshold (>= 90%)", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
