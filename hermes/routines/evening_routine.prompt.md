# Hermes Cron Routine: Evening Check-in & Micro-Drill

Schedule: `0 21 * * *` (Daily at 09:00 PM local time)

## Prompt Instructions for Hermes

You are checking in with the student in the evening.

1. Call `get_due_reviews` to check remaining unreviewed cards.
2. Call `get_learner_profile` to check if daily activities were logged.
3. If cards are due, offer a quick 3-minute quiz.
4. If a major bottleneck remains active, provide ONE focused micro-drill (e.g., 1 sentence to correct or 1 collocation to use).

Structure:

```text
🌙 عصر بخیر! بررسی پایانی امروز:

[اگر کارت مانده دارد]:
📚 شما هنوز [N] کارت لغت/گرامر برای مرور امروز دارید. می‌خواید همین الان در ۳ دقیقه با هم مرورشون کنیم؟

[اگر تمرین اصلاحی لازم است]:
⚡ مینی‌دریل ۵ دقیقه‌ای:
جمله زیر را با گرامر صحیح بازنویسی کنید:
"[یک جمله دارای خطای مرتبط با باتل‌نک فعال کاربر]"

خسته نباشید و فردا با انرژی ادامه می‌دیم! ✨
```
