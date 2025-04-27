import nest_asyncio
import asyncio
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from config import TELEGRAM_TOKEN
import recipe_generator
import data_storage

# اعمال nest_asyncio
nest_asyncio.apply()

# مراحل گفتگو
ASK_PHONE, ASK_DIET, ASK_TASTE = range(3)

# شروع گفتگو
async def start(update: Update, context) -> int:
    user = update.effective_user

    await update.message.reply_text(
        f"سلام {user.first_name} عزیز! 🌟\n\n"
        "به ربات تهیه رسپی نوشیدنی ویژه نمایشگاه INOTEX2025 خوش آمدی! 🍹✨\n\n"
        "این نسخه مخصوص تهیه رسپی سریع در نمایشگاه است.\n"
        "نسخه اصلی این ربات با نام CaReMa در حال توسعه است و بزودی به صورت حرفه‌ای در کافه‌ها و رستوران‌ها استفاده خواهد شد. ☕🍽️\n\n"
        "حالا لطفاً شماره تماس خودت رو وارد کن 📞👇"
    )

    # اضافه کردن کیبورد برای راحتی
    keyboard = [[KeyboardButton("شروع مجدد /start")]]
    await update.message.reply_text("منتظر شماره تماست هستم...", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    return ASK_PHONE

# دریافت شماره تلفن
async def ask_diet(update: Update, context) -> int:
    user_phone = update.message.text
    context.user_data['user_phone'] = user_phone

    await update.message.reply_text(
        "ممنونم! 🧡\n\n"
        "آیا رژیم غذایی خاصی داری؟ (مثلاً گیاه‌خواری، وگان، بدون قند و...)\n"
        "اگر نداری، بنویس: «ندارم»."
    )
    return ASK_DIET

# دریافت رژیم غذایی
async def ask_taste(update: Update, context) -> int:
    user_diet = update.message.text
    context.user_data['user_diet'] = user_diet

    await update.message.reply_text(
        "عالیه! 😍\n\n"
        "حالا طعم مورد علاقه‌ات رو مشخص کن:\n"
        "(مثلاً شیرین، ترش، تلخ، ملایم و...)\n"
        "اگر سلیقه خاصی نداری، بنویس: «فرقی نداره»."
    )
    return ASK_TASTE

# دریافت طعم و تولید رسپی
async def generate_and_send_recipe(update: Update, context) -> int:
    selected_taste = update.message.text
    context.user_data['selected_taste'] = selected_taste

    # پیام در حال فکر کردن
    thinking_message = await update.message.reply_text('در حال فکر کردن هستم... 🤔')

    # تولید رسپی با دریافت ورودی‌های کاربر
    recipe, instructions, benefits = recipe_generator.generate_recipe(
        diet=context.user_data['user_diet'],
        taste=context.user_data['selected_taste']
    )

    # حذف پیام "در حال فکر کردن"
    await thinking_message.delete()

    # ارسال رسپی
    recipe_text = "\n".join([f"▫️ {ingredient}: {quantity}" for ingredient, quantity in recipe.items()])
    await update.message.reply_text(
        f"✨ نوشیدنی پیشنهادی مخصوص شما:\n\n"
        f"{recipe_text}\n\n"
        f"📋 طرز تهیه:\n{instructions}\n\n"
        f"🌿 خواص مواد مصرفی:\n{benefits}"
    )

    # ذخیره اطلاعات
    user_name = update.effective_user.first_name
    user_phone = context.user_data['user_phone']
    selected_drink = context.user_data.get('selected_taste', 'نامشخص')

    data_storage.store_user_data(user_name, user_phone, selected_drink, recipe)

    # سوال برای رسپی جدید
    await update.message.reply_text(
        "آیا دوست داری یک رسپی دیگه هم برات بسازم یا اطلاعات بیشتری بهت بدم؟ 😎\n\n"
        "اگر میخوای، دستور /start رو بزن یا یک پیام جدید برام بفرست."
    )

    return ConversationHandler.END

# لغو گفتگو
async def cancel(update: Update, context) -> int:
    await update.message.reply_text("گفتگو لغو شد. خوشحال می‌شم دوباره کمکت کنم! 🧡")
    return ConversationHandler.END

# تابع اصلی
async def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_diet)],
            ASK_DIET: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_taste)],
            ASK_TASTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, generate_and_send_recipe)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
