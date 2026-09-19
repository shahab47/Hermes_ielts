"""Create official Telegram forum workspace topics for Hermes IELTS (Phase P4)."""

import json
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

TOKEN = "8825491038:AAHJuZLeX95hePqk9m5M5RMbB20_d4SiS78"
CHAT_ID = "-1004391277666"

TOPICS = [
    {
        "name": "Listening 🎧",
        "intro": "🎧 **IELTS Listening Workspace**\n\nاین تاپیک اختصاصی تمرین‌های شنیداری، آزمون‌های سکشن ۱ تا ۴ و تحلیل ترنسکریپت است.\n\n💡 دستور نمونه: `یک تمرین لیسنینگ سکشن ۱ شروع کن`",
    },
    {
        "name": "Reading 📖",
        "intro": "📖 **IELTS Reading Workspace**\n\nاین تاپیک اختصاصی درک مطلب متون آکادمیک، تست‌های TFNG، هدینگ‌ها و تحلیل سرعت خواندن (WPM) است.\n\n💡 دستور نمونه: `یک متن ریدینگ آکادمیک با سوالات TFNG بفرست`",
    },
    {
        "name": "Writing ✍️",
        "intro": "✍️ **IELTS Writing Workspace**\n\nاین تاپیک اختصاصی ارزیابی مقالات Task 1 و Task 2، تصحیح خطاهای گرامری و پیشنهاد بازنویسی ارتقادهنده بند است.\n\n💡 دستور نمونه: مقاله‌تان را بفرستید و بنویسید `این رایتینگ تسک ۲ را ارزیابی کن`",
    },
    {
        "name": "Speaking 🎙️",
        "intro": "🎙️ **IELTS Speaking Workspace**\n\nاین تاپیک اختصاصی تمرین‌های گفتاری Part 1, 2, 3 و دریافت بازخورد روانی کلام و تلفظ است.\n\n💡 دستور نمونه: `یک موضوع Speaking Part 2 با تایمر آماده‌سازی برام بفرست`",
    },
    {
        "name": "Vocabulary 📚",
        "intro": "📚 **Vocabulary & Lexical Resource Workspace**\n\nاین تاپیک اختصاصی یادگیری واژگان آکادمیک، همایندها (Collocations) و مرور مبتنی بر الگوریتم FSRS است.\n\n💡 دستور نمونه: `کلمات آکادمیک موضوع محیط زیست را تمرین کنیم`",
    },
    {
        "name": "Grammar 📝",
        "intro": "📝 **Grammar Mastery Workspace**\n\nاین تاپیک اختصاصی تمرین ساختارهای پیچیده، تبدیل جملات، وارونگی و رفع خطاهای پرتکرار است.\n\n💡 دستور نمونه: `ساختارهای گرامری برای نمره ۷ به بالا را تمرین کنیم`",
    },
    {
        "name": "Review 🔄",
        "intro": "🔄 **Spaced Review & Retention Workspace**\n\nاین تاپیک اختصاصی صف مرورهای دوره‌ای فلش‌کارت‌ها و رفع نقاط ضعف فعال شماست.\n\n💡 دستور نمونه: `/review` یا `نوبت مرور امروز من چیست؟`",
    },
    {
        "name": "Mock Exams ⏱️",
        "intro": "⏱️ **Full Timed Mock Exam Workspace**\n\nاین تاپیک اختصاصی شبیه‌سازی کامل و زمان‌بندی‌شده آزمون ماک آیلتس با گزارش جامع نمرات و کارنامه رسمی است.\n\n💡 دستور نمونه: `یک آزمون ماک کامل برای من شروع کن`",
    },
    {
        "name": "Progress 📊",
        "intro": "📊 **Learner Dashboard & Progress Workspace**\n\nاین تاپیک اختصاصی مشاهده گزارش وضعیت پیشرفت، نقاط قوت و ضعف و تخمین بند اسکور شماست.\n\n💡 دستور نمونه: `/progress` یا `خلاصه پیشرفت هفتگی من را نشان بده`",
    },
    {
        "name": "Coding 💻",
        "intro": "💻 **Hermes Self-Engineering & Codebase Development Workspace**\n\nاین تاپیک آزمایشگاه اختصاصی خودتوسعه‌ای و مهندسی سیستم هرمس است. هرمس در اینجا به عنوان مهندس ارشد نرم‌افزار، کدهای پروژه خود (`ielts-hermes`) را تحلیل، تست، دیباگ و بهینه‌سازی می‌کند و نقاط ضعف سیستم آموزشی و معماری خود را بهبود می‌بخشد.\n\n💡 دستورهای نمونه:\n• `وضعیت تست‌های خودت را بررسی و اجرا کن`\n• `کدهای ماژول ارزیابی رایتینگ را بررسی و بهینه‌سازی کن`\n• `لاگ‌های خطای اخیر سیستم را تحلیل کن و راهکار بده`\n• `گیت استاتوس و تغییرات اخیر سورس‌کد را گزارش بده`",
    },
]


def post_telegram(endpoint: str, data: dict) -> dict:
    url = f"https://api.telegram.org/bot{TOKEN}/{endpoint}"
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    print(f"Creating forum topics for chat {CHAT_ID}...")
    created = []
    for item in TOPICS:
        try:
            res = post_telegram("createForumTopic", {"chat_id": CHAT_ID, "name": item["name"]})
            thread_id = res["result"]["message_thread_id"]
            print(f"  [OK] Created topic: '{item['name']}' (thread_id: {thread_id})")

            # Send pinned/introductory message
            post_telegram(
                "sendMessage",
                {
                    "chat_id": CHAT_ID,
                    "message_thread_id": thread_id,
                    "text": item["intro"],
                    "parse_mode": "Markdown",
                },
            )
            created.append({"name": item["name"], "thread_id": thread_id})
            time.sleep(0.5)
        except Exception as e:
            print(f"  [ERR] Failed for {item['name']}: {e}")

    print("\nAll topics successfully created and initialized!")


if __name__ == "__main__":
    main()
