"""Copy of Phase 22 coding agent regression test suite for evals/runner."""
from pathlib import Path
import sys

repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(repo_root / "apps" / "learning-service"))

from tests.test_p22_coding_agent import *
