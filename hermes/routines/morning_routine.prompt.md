# Hermes Cron Routine: Morning Study Briefing

Schedule: `0 8 * * *` (Daily at 08:00 AM local time)

## Prompt Instructions for Hermes

You are sending the daily morning briefing to the student via Telegram.

1. Call the MCP tool `get_learner_profile` with the student's ID to fetch target band and status.
2. Call the MCP tool `get_due_reviews` to see how many spaced repetition items are due today.
3. Call the MCP tool `get_skill_state` or `get_learning_priorities` to identify the current top bottleneck.
4. Compose a warm, concise message in Farsi (فارسی) with this exact structure:

```text
🌅 صبح بخیر! برنامه مطالعه امروز شما:

🎯 هدف امروز: [یک جمله شفاف درباره فوکوس امروز مثلاً: برطرف کردن ضعف ساختار پاراگراف در رایتینگ تسک ۲]
⏳ زمان تخمینی: ۳۰ الی ۴۵ دقیقه

📋 کارهای امروز:
۱. مرور فلش‌کارت‌های تکرار فاصله‌دار: [تعداد] واژه و گرامر آماده مرور
۲. تمرین هدفمند: [تمرین مشخص مربوط به باتل‌نک اصلی]
۳. تمرین ترکیبی: [یک تمرین اسپیکینگ یا رایتینگ زمان‌دار]

هروقت آماده بودید، دستور "شروع تمرین" یا پیام صوتی‌تون رو بفرستید! 💪
```

5. Keep it concise. Do not overwhelm with excessive details.
