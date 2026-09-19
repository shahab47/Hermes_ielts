"""Unit tests for acoustic speech metrics and temporal fluency calculation (Phase 10)."""

from __future__ import annotations

from app.services.speech_metrics import SpeechMetricsAnalyzer, TimestampSegment


def test_speech_metrics_normal_fluent_response() -> None:
    """Test fluent speech with realistic pauses and words."""
    segments = [
        TimestampSegment(text="Well, the first person that comes to mind", start=0.0, end=2.8),
        TimestampSegment(text="is my elder cousin Daniel who is an architect.", start=3.3, end=6.5),  # 0.5s pause
        TimestampSegment(
            text="He has boundless energy and wakes up early every day.", start=7.0, end=11.2
        ),  # 0.5s pause
        TimestampSegment(
            text="Even after a grueling nine-hour workday at his firm,", start=11.6, end=15.4
        ),  # 0.4s pause
        TimestampSegment(
            text="he regularly coaches young teenagers at a boxing club.", start=15.9, end=20.0
        ),  # 0.5s pause
    ]

    metrics = SpeechMetricsAnalyzer.analyze_from_segments(segments, total_duration=20.0)

    assert metrics.duration_seconds == 20.0
    assert metrics.word_count >= 30
    assert metrics.pause_count == 4
    assert metrics.pause_ratio < 0.25
    assert metrics.speech_rate_wpm > 100.0
    assert metrics.fluency_band_estimate >= 7.0


def test_speech_metrics_hesitant_response_with_fillers() -> None:
    """Test hesitant speech with fillers and long pauses."""
    segments = [
        TimestampSegment(text="Um I think that uh", start=0.0, end=2.5),
        TimestampSegment(text="quiet places are uh very good", start=4.0, end=7.0),  # 1.5s pause
        TimestampSegment(text="because you know people need rest.", start=8.8, end=12.0),  # 1.8s pause
    ]

    metrics = SpeechMetricsAnalyzer.analyze_from_segments(segments, total_duration=12.0)

    assert metrics.duration_seconds == 12.0
    assert metrics.pause_count == 2
    assert metrics.total_pause_duration >= 3.0
    assert metrics.pause_ratio > 0.25
    assert metrics.filler_word_count >= 2
    assert "um" in metrics.filler_words_detected
    assert metrics.fluency_band_estimate <= 6.0


def test_speech_metrics_empty_segments() -> None:
    """Test graceful handling of empty segments."""
    metrics = SpeechMetricsAnalyzer.analyze_from_segments([])
    assert metrics.word_count == 0
    assert metrics.duration_seconds == 0.0
    assert metrics.speech_rate_wpm == 0.0
