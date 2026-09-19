"""Audio temporal and acoustic speech metrics extractor for IELTS Speaking (Phase 10)."""

from __future__ import annotations

import re

from pydantic import BaseModel, Field


class TimestampSegment(BaseModel):
    """Word or segment timestamp from STT (e.g., faster-whisper)."""

    text: str
    start: float = Field(ge=0.0)
    end: float = Field(ge=0.0)


class SpeechAcousticMetrics(BaseModel):
    """Calculated temporal and fluency metrics for an IELTS Speaking response."""

    duration_seconds: float = Field(ge=0.0)
    word_count: int = Field(ge=0)
    speech_rate_wpm: float = Field(ge=0.0, description="Gross words per minute")
    articulation_rate_wpm: float = Field(ge=0.0, description="Words per minute of active phonation (excluding pauses)")
    total_pause_duration: float = Field(ge=0.0, description="Cumulative silence in seconds")
    pause_ratio: float = Field(ge=0.0, le=1.0, description="Pause time as proportion of total duration")
    pause_count: int = Field(ge=0, description="Number of pauses exceeding threshold")
    filler_word_count: int = Field(ge=0, description="Count of verbal fillers (um, uh, er, etc.)")
    filler_words_detected: list[str] = []
    fluency_band_estimate: float = Field(ge=0.0, le=9.0, description="Objective fluency benchmark guide")


class SpeechMetricsAnalyzer:
    """Computes deterministic temporal fluency metrics from audio segments and timestamps."""

    # Silence threshold in seconds to qualify as a hesitation/pause
    PAUSE_THRESHOLD_SECONDS = 0.35

    # Verbal fillers common in language learner speech
    FILLER_WORDS = {"um", "uh", "er", "ah", "like", "you know", "i mean", "sort of", "kind of", "basically"}

    @classmethod
    def analyze_from_segments(
        cls,
        segments: list[TimestampSegment],
        total_duration: float | None = None,
    ) -> SpeechAcousticMetrics:
        """Calculate temporal speech metrics from timestamped STT segments."""
        if not segments:
            return SpeechAcousticMetrics(
                duration_seconds=0.0,
                word_count=0,
                speech_rate_wpm=0.0,
                articulation_rate_wpm=0.0,
                total_pause_duration=0.0,
                pause_ratio=0.0,
                pause_count=0,
                filler_word_count=0,
                fluency_band_estimate=4.0,
            )

        # 1. Total duration
        calc_duration = segments[-1].end - segments[0].start
        duration = total_duration if total_duration is not None and total_duration > 0 else max(calc_duration, 1.0)

        # 2. Extract text and words
        full_text = " ".join(s.text for s in segments)
        words = re.findall(r"\b[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*\b", full_text.lower())
        word_count = len(words)

        # 3. Detect pauses between segments
        pause_count = 0
        total_pause_sec = 0.0

        for i in range(len(segments) - 1):
            gap = segments[i + 1].start - segments[i].end
            if gap >= cls.PAUSE_THRESHOLD_SECONDS:
                pause_count += 1
                total_pause_sec += gap

        # 4. Fillers
        detected_fillers: list[str] = []
        for word in words:
            if word in cls.FILLER_WORDS:
                detected_fillers.append(word)

        # 5. Rates
        duration_minutes = duration / 60.0
        active_speech_minutes = max((duration - total_pause_sec) / 60.0, 0.05)

        speech_rate_wpm = round(word_count / duration_minutes, 1)
        articulation_rate = round(word_count / active_speech_minutes, 1)
        pause_ratio = round(min(total_pause_sec / duration, 1.0), 3)

        # 6. Objective fluency band estimate guideline:
        # Native/C2: 130-160 WPM, pause ratio < 0.20 -> Band 8.5-9.0
        # Competent/B2: 100-130 WPM, pause ratio 0.20-0.30 -> Band 6.5-7.5
        # Modest/B1: 70-100 WPM, pause ratio 0.30-0.45 -> Band 5.0-6.0
        # Limited: < 70 WPM, pause ratio > 0.45 -> Band 4.0-4.5
        if speech_rate_wpm >= 135 and pause_ratio < 0.20 and len(detected_fillers) < 3:
            est_band = 8.0
        elif speech_rate_wpm >= 110 and pause_ratio < 0.28:
            est_band = 7.0
        elif speech_rate_wpm >= 85 and pause_ratio < 0.38:
            est_band = 6.0
        elif speech_rate_wpm >= 65:
            est_band = 5.0
        else:
            est_band = 4.0

        return SpeechAcousticMetrics(
            duration_seconds=round(duration, 2),
            word_count=word_count,
            speech_rate_wpm=speech_rate_wpm,
            articulation_rate_wpm=articulation_rate,
            total_pause_duration=round(total_pause_sec, 2),
            pause_ratio=pause_ratio,
            pause_count=pause_count,
            filler_word_count=len(detected_fillers),
            filler_words_detected=detected_fillers,
            fluency_band_estimate=est_band,
        )
