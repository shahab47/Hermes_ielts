"""Copy of Phase 23 memory regression test suite for evals/runner."""
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(repo_root / "apps" / "learning-service"))

from tests.test_p23_memory_regression import *
