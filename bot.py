import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import config
import response
import recipe_generator
import data_storage

# فعال کردن لاگ‌گذاری برای خطاها و اطلاع‌رسانی
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# دستور شروع ربات
def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"سلام {user.first_name} عزیز! به ربات Inotexdrinkbot خوش آمدید.\n"
             "برای شروع انتخاب نوشیدنی سرد خود، لطفاً چند سوال را پاسخ دهید."
    )
    ask_user_preferences(update, context)

# پرسش از کاربر برای دریافت اطلاعات اولیه (رژیم غذایی، حساسیت‌ها و سلیقه)
def ask_user_preferences(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="آیا حساسیت غذایی خاصی دارید؟ (مثل شیر، گندم، گلوتن، ...) یا گزینه 'ندارم' را وارد کنید."
    )
    
    # بعد از این که کاربر پاسخ داد، به مرحله بعدی رفته و رسیپی نوشیدنی را تولید می‌کند
    return

# پردازش پاسخ کاربر برای سوالات
def handle_user_input(update: Update, context: CallbackContext) -> None:
    user_input = update.message.text.lower()
    
    if 'ندارم' in user_input:
        response_text = "ممنون که به ما اطلاع دادید. حالا بیایید سلیقه‌تون رو بگید!"
    else:
        response_text = "آیا شما علاقه دارید نوشیدنی‌هایی با طعم میوه یا گیاهی داشته باشید؟"
    
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response_text
    )

    # بعد از پردازش سوالات، کاربر به مرحله انتخاب نوشیدنی هدایت می‌شود
    return

# دریافت رسیپی نهایی
def send_recipe(update: Update, context: CallbackContext) -> None:
    # لیست مواد موجود از قبل باید در `recipe_generator` باشد.
    recipe = recipe_generator.generate_recipe()
    
    recipe_text = "\n".join([f"{ingredient}: {quantity}" for ingredient, quantity in recipe.items()])
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"رسپی شما:\n{recipe_text}"
    )

    # ذخیره‌سازی اطلاعات کاربر و نوشیدنی نهایی
    data_storage.save_user_data(update.effective_user, recipe)

# متد اصلی برای راه‌اندازی ربات
def main() -> None:
    # استفاده از توکن ربات که در config.py ذخیره شده است
    updater = Updater(token=config.TOKEN)

    dispatcher = updater.dispatcher

    # ثبت دستورات مختلف
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_user_input))

    # شروع ربات
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
