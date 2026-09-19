"""Unit tests for FSRS scheduling and vocabulary filtering (Phase 9)."""

from __future__ import annotations

from datetime import UTC, datetime

from app.fsrs import (
    FSRSAdapter,
    FSRSItemState,
    ItemCandidate,
    VocabularyFilter,
)
from app.models.learning_item import ItemType, MasteryState, ReviewRating


def test_fsrs_review_progression() -> None:
    """Test standard FSRS progression from initial review to reviewing state."""
    now = datetime.now(UTC)
    card = FSRSItemState(last_review=now, due=now)

    # First review: Good
    res1 = FSRSAdapter.process_review(card, ReviewRating.GOOD, review_time=now)
    assert res1.updated_state.reps == 1
    assert res1.updated_state.scheduled_days >= 2
    assert res1.next_due_date > now

    # Second review: Good -> graduates to Reviewing
    res2 = FSRSAdapter.process_review(res1.updated_state, ReviewRating.GOOD, review_time=res1.next_due_date)
    assert res2.updated_state.reps == 2
    assert res2.updated_state.scheduled_days >= 4

    # Lapse: Again -> resets interval to 1 day, marks lapsed
    res3 = FSRSAdapter.process_review(res2.updated_state, ReviewRating.AGAIN, review_time=res2.next_due_date)
    assert res3.updated_state.lapses == 1
    assert res3.updated_state.scheduled_days == 1
    assert res3.mastery_state == MasteryState.LAPSED


def test_vocabulary_filter_rejection_of_incidental_words() -> None:
    """Incidental words without errors or academic significance are rejected."""
    cand = ItemCandidate(
        canonical_form="apple",
        item_type=ItemType.VOCABULARY,
        occurrence_count=1,
        has_learner_error=False,
    )
    decision = VocabularyFilter.evaluate_candidate(cand)
    assert not decision.is_accepted


def test_vocabulary_filter_acceptance_of_error_and_request() -> None:
    """Words with learner errors or explicit requests are admitted to FSRS."""
    # With error
    err_cand = ItemCandidate(
        canonical_form="substantially",
        item_type=ItemType.VOCABULARY,
        has_learner_error=True,
    )
    d1 = VocabularyFilter.evaluate_candidate(err_cand)
    assert d1.is_accepted
    assert d1.reason is not None and d1.reason.value == "repeated_error"

    # With user request
    req_cand = ItemCandidate(
        canonical_form="ubiquitous",
        item_type=ItemType.VOCABULARY,
        is_explicit_request=True,
    )
    d2 = VocabularyFilter.evaluate_candidate(req_cand)
    assert d2.is_accepted
    assert d2.reason is not None and d2.reason.value == "user_request"
