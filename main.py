import os
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from openai import OpenAI

# 🔐 قراءة التوكنات من النظام (مو مكتوبة بالكود)
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN غير موجود")
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY غير موجود")

# حساب الادمن
ADMIN_ID = 6632799705  # ايدي حسابك

# القنوات المطلوبة (بدون @)
REQUIRED_CHANNELS = ["EETFR"]

client = OpenAI(api_key=OPENAI_API_KEY)

# تحديد اللغة
def detect_language(text):
    if re.search(r'[\u0600-\u06FF]', text):
        return "arabic"
    return "english"

async def ai_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    username = user.username or "NoUsername"
    first_name = user.first_name or "NoName"

    # تحقق الاشتراك
    subscribed = True
    for channel in REQUIRED_CHANNELS:
        try:
            member = await context.bot.get_chat_member(
                chat_id=f"@{channel}",
                user_id=user_id
            )
            if member.status in ["left", "kicked"]:
                subscribed = False
        except:
            subscribed = False

    # تقرير للإدمن
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"👤 User: {first_name} (@{username})\n"
            f"🆔 ID: {user_id}\n"
            f"📢 Subscribed: {subscribed}"
        )
    )

    if not subscribed:
        await update.message.reply_text(
            f"هلا {first_name} 🙏\n"
            "اشترك بالقناة التالية أولاً:\n"
            + "\n".join([f"@{ch}" for ch in REQUIRED_CHANNELS])
        )
        return

    # رسالة المستخدم
    user_message = update.message.text
    language = detect_language(user_message)

    if language == "arabic":
        system_prompt = "أنت مساعد ذكي يرد باللهجة العراقية وبأسلوب لطيف."
    else:
        system_prompt = "You are a smart assistant. Reply in English politely."

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    )

    reply = response.choices[0].message.content
    await update.message.reply_text(reply)

# تشغيل البوت
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_reply))

print("🤖 Bot running...")
app.run_polling()
