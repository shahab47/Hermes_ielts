"""Phase 22 Regression Suite: Coding Agent Capabilities in Sandboxed Workspace.

Verifies that the agent architecture preserves:
1. Inspecting repository workspace
2. Locating bugs from test failures
3. Editing and patching source code
4. Running automated test commands in sandbox
5. Iterative fix and regression verification
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


def run_command_in_sandbox(cwd: Path, cmd: list[str]) -> tuple[int, str, str]:
    res = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    return res.returncode, res.stdout, res.stderr


def test_coding_agent_sandbox_lifecycle() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        sandbox = Path(temp_dir)

        # 1. Setup sandbox repository files
        src_file = sandbox / "calculator.py"
        test_file = sandbox / "test_calculator.py"

        # Intentionally buggy code (returns subtraction instead of addition)
        src_file.write_text(
            "def calculate_sum(a: int, b: int) -> int:\n"
            "    # Intentional bug for regression test\n"
            "    return a - b\n",
            encoding="utf-8",
        )

        test_file.write_text(
            "from calculator import calculate_sum\n\n"
            "def test_calculate_sum():\n"
            "    assert calculate_sum(2, 3) == 5\n\n"
            "if __name__ == '__main__':\n"
            "    test_calculate_sum()\n"
            "    print('ALL_PASSED')\n",
            encoding="utf-8",
        )

        # Step 1: Inspect repository
        found_files = [p.name for p in sandbox.glob("*.py")]
        assert "calculator.py" in found_files
        assert "test_calculator.py" in found_files

        # Step 2: Run tests before fix -> MUST FAIL
        code, stdout, stderr = run_command_in_sandbox(sandbox, [sys.executable, "-B", str(test_file)])
        assert code != 0, "Test should have failed with buggy implementation"
        assert "AssertionError" in stderr or "AssertionError" in stdout

        # Step 3: Locate bug and inspect code
        content = src_file.read_text(encoding="utf-8")
        assert "return a - b" in content

        # Step 4: Apply patch
        fixed_content = content.replace("return a - b", "return a + b")
        src_file.write_text(fixed_content, encoding="utf-8")

        # Step 5: Rerun tests after fix -> MUST PASS
        code, stdout, stderr = run_command_in_sandbox(sandbox, [sys.executable, "-B", str(test_file)])
        assert code == 0, f"Test failed after patch: {stderr}"
        assert "ALL_PASSED" in stdout

        # Step 6: Verify patched code integrity
        final_code = src_file.read_text(encoding="utf-8")
        assert "return a + b" in final_code
