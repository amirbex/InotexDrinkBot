# main.py

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from utils import generate_recipe, save_user_data
from telegram import ParseMode

# توکن ربات
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    update.message.reply_text(
        f"سلام {user.first_name}! خوش آمدید به ربات مشاوره نوشیدنی سرد. 🌟\n\n"
        "من به شما کمک می‌کنم تا بهترین نوشیدنی سرد با مواد موجود رو پیدا کنید.\n"
        "لطفاً برای شروع، چند سوال در مورد عادات غذایی و حساسیت‌های شما دارم.\n\n"
        "به من بگویید که آیا شما رژیم خاصی دارید یا حساسیت به مواد خاصی دارید؟"
    )

def handle_message(update: Update, context: CallbackContext):
    text = update.message.text.lower()

    if "رژیم" in text or "حساسیت" in text:
        update.message.reply_text(
            "خیلی خوب! من در حال پردازش اطلاعات شما هستم. لطفاً چند دقیقه صبر کنید...\n"
            "من یک نوشیدنی مناسب برای شما پیدا می‌کنم!"
        )
        final_drink = generate_recipe()
        update.message.reply_text(
            f"نوشیدنی پیشنهادی شما: \n{final_drink}",
            parse_mode=ParseMode.MARKDOWN
        )
        save_user_data(update.message.from_user.first_name, update.message.from_user.id, final_drink)

    else:
        update.message.reply_text(
            "ممنون از پاسخ شما! برای ادامه، لطفاً اطلاعات بیشتری بدهید یا سوالی بپرسید."
        )

def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # دکمه های اصلی
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
