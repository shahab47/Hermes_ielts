"""Source-Aware Question Delivery Engine (Phase P16).

Transforms domain Question entities into channel-independent delivery payloads
and Telegram-compatible presentations (inline keyboards, audio attachments, timed prompts).
"""

from __future__ import annotations

from typing import Any

from app.domain.question_bank import (
    DeliveryModality,
    DeliveryPayload,
    ListeningQuestionType,
    Question,
    ReadingQuestionType,
    SpeakingPartType,
    WritingTaskType,
)
from app.models.learner import Skill


class QuestionDeliveryService:
    """Channel-independent question formatter and serializer."""

    @classmethod
    def format_for_delivery(cls, question: Question) -> DeliveryPayload:
        """Determines proper delivery modality and prepares presentation structure."""
        skill = question.skill
        q_type = question.question_type
        modality = DeliveryModality.TEXT
        display_options: list[dict[str, str]] = []
        matching_pairs: dict[str, list[str]] | None = None
        audio_uri: str | None = None
        image_uri: str | None = None
        requires_timer = False
        timer_seconds: int | None = None
        requires_long_form = False

        # Check media attachments
        for m in question.media:
            if m.media_type == "audio" and not audio_uri:
                audio_uri = m.uri
            elif m.media_type in ("image", "diagram") and not image_uri:
                image_uri = m.uri

        # 1. Speaking Modality
        if skill == Skill.SPEAKING:
            modality = DeliveryModality.VOICE_PROMPT
            requires_timer = True
            if q_type == SpeakingPartType.PART_2:
                timer_seconds = 60  # 1-minute prep time
            elif q_type == SpeakingPartType.PART_1:
                timer_seconds = 15
            else:
                timer_seconds = 30

        # 2. Writing Modality
        elif skill == Skill.WRITING:
            modality = DeliveryModality.LONG_FORM
            requires_long_form = True
            requires_timer = True
            timer_seconds = 20 * 60 if q_type == WritingTaskType.TASK_1 else 40 * 60

        # 3. Listening with Audio Modality
        elif skill == Skill.LISTENING and audio_uri:
            modality = DeliveryModality.AUDIO_WITH_PROMPTS
            if question.options:
                display_options = [{"key": opt.key, "label": opt.text} for opt in question.options]

        # 4. MCQ Modalities
        elif q_type in (
            ListeningQuestionType.MCQ_SINGLE,
            ListeningQuestionType.MCQ_MULTIPLE,
            ReadingQuestionType.MCQ,
            ReadingQuestionType.TFNG,
            ReadingQuestionType.YNNG,
        ) or bool(question.options):
            modality = DeliveryModality.OPTIONS
            if question.options:
                display_options = [{"key": opt.key, "label": opt.text} for opt in question.options]
            elif q_type == ReadingQuestionType.TFNG:
                display_options = [
                    {"key": "TRUE", "label": "True"},
                    {"key": "FALSE", "label": "False"},
                    {"key": "NOT GIVEN", "label": "Not Given"},
                ]
            elif q_type == ReadingQuestionType.YNNG:
                display_options = [
                    {"key": "YES", "label": "Yes"},
                    {"key": "NO", "label": "No"},
                    {"key": "NOT GIVEN", "label": "Not Given"},
                ]

        # 5. Matching Modalities
        elif q_type in (
            ListeningQuestionType.MATCHING,
            ReadingQuestionType.MATCHING_HEADINGS,
            ReadingQuestionType.MATCHING_INFORMATION,
            ReadingQuestionType.MATCHING_FEATURES,
        ):
            modality = DeliveryModality.MATCHING_PAIRS
            if question.options:
                display_options = [{"key": opt.key, "label": opt.text} for opt in question.options]

        # 6. Text / Completion Modalities
        else:
            modality = DeliveryModality.TEXT

        return DeliveryPayload(
            question_id=question.id,
            modality=modality,
            prompt_text=question.prompt,
            instructions=question.instructions,
            display_options=display_options,
            matching_pairs_definition=matching_pairs,
            audio_uri=audio_uri,
            image_uri=image_uri,
            requires_timer=requires_timer,
            timer_seconds=timer_seconds,
            requires_long_form=requires_long_form,
            metadata={
                "skill": skill.value,
                "task_type": question.task_type,
                "question_type": q_type,
                "difficulty": question.difficulty.value,
                "cefr": question.cefr.value if question.cefr else None,
            },
        )

    @classmethod
    def render_telegram_message(cls, payload: DeliveryPayload) -> dict[str, Any]:
        """Renders payload into Telegram-friendly text formatting and inline keyboards."""
        lines = []
        if payload.instructions:
            lines.append(f"ℹ️ *Instructions:* {payload.instructions}\n")  # noqa: RUF001
        lines.append(f"❓ *Question:*\n{payload.prompt_text}")

        reply_markup: dict[str, Any] | None = None

        if payload.modality == DeliveryModality.OPTIONS and payload.display_options:
            keyboard = []
            for opt in payload.display_options:
                keyboard.append([{"text": f"{opt['key']}: {opt['label']}", "callback_data": f"ans_{opt['key']}"}])
            reply_markup = {"inline_keyboard": keyboard}

        elif payload.modality == DeliveryModality.VOICE_PROMPT:
            if payload.timer_seconds:
                lines.append(f"\n⏱ *Preparation Time:* {payload.timer_seconds} seconds")
            lines.append("🎙 *Please reply with a voice message.*")

        elif payload.modality == DeliveryModality.LONG_FORM:
            if payload.timer_seconds:
                minutes = payload.timer_seconds // 60
                lines.append(f"\n⏱ *Target Duration:* {minutes} minutes")
            lines.append("✍️ *Submit your essay in a single text message.*")

        elif payload.modality == DeliveryModality.AUDIO_WITH_PROMPTS:
            lines.append("\n🎧 *Listen to the audio track and record your answer.*")
            if payload.display_options:
                keyboard = [
                    [{"text": f"{opt['key']}: {opt['label']}", "callback_data": f"ans_{opt['key']}"}]
                    for opt in payload.display_options
                ]
                reply_markup = {"inline_keyboard": keyboard}

        return {
            "text": "\n".join(lines),
            "reply_markup": reply_markup,
            "audio_uri": payload.audio_uri,
            "modality": payload.modality.value,
        }
