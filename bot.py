import logging
import openai
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# فعال کردن لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# توکن جمینای
openai.api_key = "AIzaSyC8VK_y5ESVLZNXI80wy7KBJ5_IxEoxh7E"

# استیج‌های مکالمه
ASK_PHONE, ASK_PREFERENCES, SEND_RECIPE, CHAT_AFTER_RECIPE = range(4)

# دکمه‌های ثابت
keyboard = [
    [KeyboardButton("▶️ شروع مجدد"), KeyboardButton("🧃 رسپی جدید")]
]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# مواد اولیه
SYRUPS = [
    "پاپ کرن", "بلک بری", "گرانادین", "زعفران", "خیار", "گرین میکس", "وانیل",
    "شکلات", "آیریش", "ردمیکس", "پشن فروت", "رام", "آدامس آبی", "گواوا",
    "ویمتو", "کوکی", "فندق", "بادیان", "چای تی"
]

JUICES = [
    "آلبالو", "آبلیمو طبیعی", "پرتقال", "میکس کرنبری گریپ فروت", "آناناس",
    "آناناس استار فروت", "آب گوجه", "کیوی لیمو", "سیب سبز", "هلو",
    "انبه", "انگور سفید", "انگور سیاه", "سودا گازدار"
]

FRUITS = [
    "ریحان ایتالیایی", "لیمو زرد", "گل خوراکی", "نعنا تازه", "توت فرنگی", "پرتقال تازه"
]

HERBS = [
    "کاسنی", "بیدمشک", "بهارنارنج"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # پیام اول: احوالپرسی
    await update.message.reply_text(f"سلام {user.first_name}! 👋")

    # پیام دوم: معرفی
    await update.message.reply_text(
        "من دستیار هوشمند تهیه دستورالعمل نوشیدنی در غرفه‌ی اکسیر در نمایشگاه اینوتکس 2025 هستم!\n"
        "این ربات یک نمونه اولیه از یک طرح در حال توسعه است.\n"
        "من اینجا با چند تا سوال خیلی سریع بهت یه دستورالعمل تهیه نوشیدنی میدم. 🍹🎉"
    )

    # پیام سوم: درخواست شماره موبایل
    await update.message.reply_text(
        "خوشحالم که اینجایی! برای شروع لطفاً شماره موبایلت رو وارد کن 📱",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("ارسال شماره تلفن", request_contact=True)]], resize_keyboard=True)
    )

    return ASK_PHONE

async def ask_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # دریافت شماره موبایل
    if update.message.contact:
        phone_number = update.message.contact.phone_number
        context.user_data['phone_number'] = phone_number
        await update.message.reply_text("ممنونم! حالا آماده‌ایم برای ساخت یه نوشیدنی عالی! 🥂")
    else:
        await update.message.reply_text("لطفاً شماره موبایلت رو از طریق دکمه ارسال کن. 📱")
        return ASK_PHONE

    await update.message.reply_text("بگو طعمی که دوست داری چیه؟ ترش، شیرین یا خاص؟")
    return ASK_PREFERENCES

async def send_recipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_pref = update.message.text

    import random

    recipe = []
    total_volume = 0

    # اضافه کردن سیروپ‌ها (با رعایت حجم حداکثر ۵۰ میل)
    syrup = random.choice(SYRUPS)
    syrup_volume = random.randint(20, 50)
    total_volume += syrup_volume
    recipe.append(f"{syrup_volume}ml سیروپ {syrup}")

    # اضافه کردن آبمیوه‌ها
    for _ in range(2):
        juice = random.choice(JUICES)
        juice_volume = random.randint(50, 80)
        total_volume += juice_volume
        recipe.append(f"{juice_volume}ml آب {juice}")

    # اضافه کردن میوه یا سبزی تازه
    fruit = random.choice(FRUITS)
    recipe.append(f"مقداری {fruit} تازه 🍃")

    # اضافه کردن عرقیات
    herb = random.choice(HERBS)
    recipe.append(f"چند قطره عرق {herb}")

    # بالانس حجم تا ۲۸۰ میل
    if total_volume < 280:
        remaining = 280 - total_volume
        recipe.append(f"{remaining}ml آب سودا یا آب ساده")

    # ارسال رسپی
    await update.message.reply_text(
        f"🥤 رسپی پیشنهادی برای تو:\n\n" +
        "\n".join(recipe) +
        "\n\n✨ طرز تهیه: همه مواد رو تو شیکر با یخ مخلوط کن و سرو کن!"
    )

    # ارسال پیام به جمینای برای دریافت خواص
    response = openai.ChatCompletion.create(
        model="gpt-4",  # اگر مدل جمینای مشابه باشد
        messages=[
            {"role": "system", "content": "شما یک دستیار هوش مصنوعی برای ارائه خواص نوشیدنی‌ها هستید."},
            {"role": "user", "content": f"چه خواصی دارد ترکیب {', '.join(recipe)}؟"},
        ]
    )
    gemini_reply = response['choices'][0]['message']['content']
    await update.message.reply_text(gemini_reply)

    await update.message.reply_text(
        "خواص ترکیب: افزایش انرژی، طراوت پوست، نشاط ذهنی! 🌿✨",
        reply_markup=reply_markup
    )

    return CHAT_AFTER_RECIPE

async def chat_after_recipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    if user_text == "▶️ شروع مجدد":
        return await start(update, context)
    if user_text == "🧃 رسپی جدید":
        await update.message.reply_text("باشه! سوال جدید: چه طعمی دوست داری؟ 🍋🍫🌸")
        return ASK_PREFERENCES

    # پاسخ به سوالات کاربر در مورد رسپی
    await update.message.reply_text("در مورد رسپی سوال داری؟ بپرس! 🍹 من اینجام برای جواب دادن. ✨")

    return CHAT_AFTER_RECIPE

async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("لطفاً از گزینه‌های موجود استفاده کن 🙏")

def main():
    app = ApplicationBuilder().token("7843819663:AAED6HyqaLKdANVHq3kvqvYua9koAJp14Ts").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_PHONE: [MessageHandler(filters.CONTACT, ask_preferences), MessageHandler(filters.TEXT, ask_preferences)],
            ASK_PREFERENCES: [MessageHandler(filters.TEXT & ~filters.COMMAND, send_recipe)],
            CHAT_AFTER_RECIPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, chat_after_recipe)],
        },
        fallbacks=[MessageHandler(filters.COMMAND, fallback)]
    )

    app.add_handler(conv_handler)

    app.run_polling()

if __name__ == "__main__":
    main()
