#!/usr/bin/env python3
"""Production release health and readiness verification script (Phase 28)."""

import argparse
import json
import sys
from urllib import request


def check_endpoint(url: str, name: str) -> bool:
    try:
        req = request.Request(url, headers={"User-Agent": "Production-Health-Checker/1.0"})
        with request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            status = data.get("status", "unknown")
            print(f"[OK] {name} ({url}): HTTP {resp.status} - Status: {status}")
            return resp.status == 200 and status in ("ok", "ready")
    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] {name} ({url}): Error - {e}", file=sys.stderr)
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify IELTS Hermes Production Health")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Base backend URL")
    args = parser.parse_args()

    print("==================================================================")
    print(" IELTS Hermes Production Release Health Verification")
    print("==================================================================")

    liveness = check_endpoint(f"{args.base_url}/health/liveness", "Liveness Probe")
    readiness = check_endpoint(f"{args.base_url}/health/readiness", "Readiness Probe")

    print("==================================================================")
    if liveness and readiness:
        print("[OK] All production service health gates PASSED.")
        return 0
    else:
        print("[!] Health checks failed. Production service is degraded.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
