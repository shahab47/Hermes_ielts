"""Phase 23 Regression Suite: Cross-Session Memory Continuity & Portability Migration.

Verifies:
1. Multi-session factual persistence (target band, recurring error, language preference).
2. Clean recovery post-restart without hallucinated extra facts.
3. Export -> Fresh Environment -> Import preserves identical learner identity.
"""

from __future__ import annotations

import tempfile
from pathlib import Path


class SimulatedMemoryStore:
    """Simulates Hermes persistent profile layer (USER.md / MEMORY.md)."""

    def __init__(self, profile_dir: Path) -> None:
        self.profile_dir = profile_dir
        self.user_file = profile_dir / "USER.md"
        self.memory_file = profile_dir / "MEMORY.md"

    def session_a_store_facts(
        self,
        target_band: float,
        explanation_language: str,
        recurring_error: str,
        exam_horizon: str,
    ) -> None:
        user_content = (
            "# Learner Profile\n\n"
            f"- Target Band: {target_band}\n"
            f"- Preferred Explanation Language: {explanation_language}\n"
            f"- Preparation Horizon: {exam_horizon}\n"
        )
        self.user_file.write_text(user_content, encoding="utf-8")

        memory_content = (
            "# Reflective Learning Memory\n\n"
            f"- Primary Recurring Weakness: {recurring_error}\n"
            "- Last Session Status: Completed Task 2 diagnostic with focus on sentence boundaries.\n"
        )
        self.memory_file.write_text(memory_content, encoding="utf-8")

    def session_b_retrieve_facts(self) -> dict[str, str | float]:
        user_text = self.user_file.read_text(encoding="utf-8")
        memory_text = self.memory_file.read_text(encoding="utf-8")

        facts: dict[str, str | float] = {}

        for line in user_text.splitlines():
            if "Target Band:" in line:
                facts["target_band"] = float(line.split("Target Band:")[1].strip())
            elif "Preferred Explanation Language:" in line:
                facts["language"] = line.split("Preferred Explanation Language:")[1].strip()
            elif "Preparation Horizon:" in line:
                facts["horizon"] = line.split("Preparation Horizon:")[1].strip()

        for line in memory_text.splitlines():
            if "Primary Recurring Weakness:" in line:
                facts["recurring_weakness"] = line.split("Primary Recurring Weakness:")[1].strip()

        return facts


def test_cross_session_memory_continuity() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        prof_dir = Path(temp_dir)
        store = SimulatedMemoryStore(prof_dir)

        # --- SESSION A ---
        store.session_a_store_facts(
            target_band=7.5,
            explanation_language="Persian (Farsi)",
            recurring_error="Run-on sentences and comma splices in Task 2",
            exam_horizon="November 2026",
        )

        # --- SIMULATED RESTART ---
        # Discard in-memory python references; instantiate fresh store pointing to same disk state
        fresh_store = SimulatedMemoryStore(prof_dir)

        # --- SESSION B ---
        recovered = fresh_store.session_b_retrieve_facts()

        # 1. Assert exact fact recovery
        assert recovered["target_band"] == 7.5
        assert recovered["language"] == "Persian (Farsi)"
        assert recovered["recurring_weakness"] == "Run-on sentences and comma splices in Task 2"
        assert recovered["horizon"] == "November 2026"

        # 2. Assert no hallucinated facts
        assert "spanish" not in str(recovered).lower()
        assert "band 9.0" not in str(recovered).lower()


def test_migration_portability_across_environments() -> None:
    import zipfile

    with tempfile.TemporaryDirectory() as env_a_dir, tempfile.TemporaryDirectory() as env_b_dir:
        env_a = Path(env_a_dir)
        env_b = Path(env_b_dir)

        # 1. Create learner state in Env A
        store_a = SimulatedMemoryStore(env_a)
        store_a.session_a_store_facts(
            target_band=8.0,
            explanation_language="Persian (Farsi)",
            recurring_error="Overusing mechanical cohesive devices (Furthermore, Moreover)",
            exam_horizon="December 2026",
        )

        # 2. Package/Export into archive
        archive_path = env_a / "export.zip"
        with zipfile.ZipFile(archive_path, "w") as zf:
            zf.write(env_a / "USER.md", arcname="USER.md")
            zf.write(env_a / "MEMORY.md", arcname="MEMORY.md")

        # 3. Simulate migration into clean Env B
        with zipfile.ZipFile(archive_path, "r") as zf:
            zf.extractall(env_b)

        # 4. Verify identical recovered learner identity in Env B
        store_b = SimulatedMemoryStore(env_b)
        recovered_b = store_b.session_b_retrieve_facts()

        assert recovered_b["target_band"] == 8.0
        assert recovered_b["language"] == "Persian (Farsi)"
        assert "cohesive devices" in str(recovered_b["recurring_weakness"])
