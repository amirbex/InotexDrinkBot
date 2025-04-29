import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import openai
import random

# فعال کردن لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# استیج‌های مکالمه
ASK_PHONE, ASK_PREFERENCES, SEND_RECIPE, CHAT_AFTER_RECIPE = range(4)

# دکمه‌های ثابت
keyboard = [
    [KeyboardButton("▶️ شروع مجدد"), KeyboardButton("🧃 رسپی جدید")]
]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# مواد اولیه
SYRUP_SIZES = [10, 25, 50, 80]
JUICE_SIZES = [10, 25, 50, 80]

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

# تنظیم توکن مدل جمینای
openai.api_key = 'AIzaSyC8VK_y5ESVLZNXI80wy7KBJ5_IxEoxh7E'

def generate_recipe():
    recipe = []
    total_volume = 0

    # انتخاب سیروپ با حجم مشخص
    syrup = random.choice(SYRUPS)
    syrup_volume = random.choice(SYRUP_SIZES)
    total_volume += syrup_volume
    recipe.append(f"{syrup_volume}ml سیروپ {syrup}")

    # انتخاب آبمیوه‌ها با حجم مشخص
    for _ in range(2):
        juice = random.choice(JUICES)
        juice_volume = random.choice(JUICE_SIZES)
        total_volume += juice_volume
        recipe.append(f"{juice_volume}ml آب {juice}")

    # انتخاب میوه تازه
    fruit = random.choice(FRUITS)
    recipe.append(f"مقداری {fruit} تازه 🍃")

    # انتخاب عرقیات
    herb = random.choice(HERBS)
    recipe.append(f"چند قطره عرق {herb}")

    # بالانس حجم تا ۲۸۰ میلی‌لیتر
    if total_volume < 280:
        remaining = 280 - total_volume
        recipe.append(f"{remaining}ml آب سودا یا آب ساده")

    return recipe

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"سلام {user.first_name}! 👋")

    await update.message.reply_text(
        "من دستیار هوشمند تهیه دستورالعمل نوشیدنی در غرفه‌ی اکسیر در نمایشگاه اینوتکس 2025 هستم!\n"
        "این ربات یک نمونه اولیه از یک طرح در حال توسعه است.\n"
        "من اینجا با چند تا سوال خیلی سریع بهت یه دستورالعمل تهیه نوشیدنی میدم. 🍹🎉"
    )

    await update.message.reply_text(
        "خوشحالم که اینجایی! برای شروع لطفاً شماره موبایلت رو وارد کن 📱",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("ارسال شماره تلفن", request_contact=True)]], resize_keyboard=True)
    )

    return ASK_PHONE

async def ask_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    recipe = generate_recipe()

    await update.message.reply_text(
        f"🥤 رسپی پیشنهادی برای تو:\n\n" +
        "\n".join(recipe) +
        "\n\n✨ طرز تهیه: همه مواد رو تو شیکر با یخ مخلوط کن و سرو کن!"
    )

    await update.message.reply_text(
        "خواص ترکیب: افزایش انرژی، طراوت پوست، نشاط ذهنی! 🌿✨",
        reply_markup=reply_markup
    )

    return CHAT_AFTER_RECIPE

async def chat_after_recipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    # Start live chat with Gemini (or similar)
    if user_text.lower() in ['رسپی جدید', 'شروع مجدد']:
        await update.message.reply_text("باشه! سوال جدید: چه طعمی دوست داری؟ 🍋🍫🌸")
        return ASK_PREFERENCES

    # Respond to questions about the recipe using ChatCompletion
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # or any other appropriate model
        messages=[
            {"role": "system", "content": "You are a helpful assistant in a bar."},
            {"role": "user", "content": user_text}
        ]
    )
    answer = response['choices'][0]['message']['content']
    
    await update.message.reply_text(answer)

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
