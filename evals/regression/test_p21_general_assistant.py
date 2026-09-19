"""Copy of Phase 21 regression test suite for evals/runner."""
import sys
from pathlib import Path

# Add apps/learning-service to sys.path
repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(repo_root / "apps" / "learning-service"))

from tests.test_p21_general_assistant import *
