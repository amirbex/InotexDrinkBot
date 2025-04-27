import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
import config
import recipe_generator
import data_storage

# فعال کردن لاگ‌گذاری
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# استیج‌های گفتگو
ASK_PHONE, ASK_DRINK = range(2)

# استارت ربات
def start(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"سلام {user.first_name} عزیز! خوش اومدی به Inotex Drink Bot 🍹\n"
             "لطفاً شماره تلفنت رو وارد کن:"
    )
    return ASK_PHONE

# دریافت شماره موبایل
def ask_drink(update: Update, context: CallbackContext) -> int:
    user_phone = update.message.text
    context.user_data['user_phone'] = user_phone

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="حالا اسم نوشیدنی مورد علاقه‌تو وارد کن یا بنویس 'فرقی نداره'."
    )
    return ASK_DRINK

# دریافت نوشیدنی و تولید رسپی
def generate_and_send_recipe(update: Update, context: CallbackContext) -> int:
    selected_drink = update.message.text
    context.user_data['selected_drink'] = selected_drink

    # ساخت رسپی
    recipe = recipe_generator.generate_recipe()
    recipe_text = "\n".join([f"{ingredient}: {quantity}" for ingredient, quantity in recipe.items()])

    # ارسال رسپی به کاربر
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"اینم نوشیدنی پیشنهادی برات:\n\n{recipe_text}"
    )

    # ذخیره اطلاعات در فایل
    user_name = update.effective_user.first_name
    user_phone = context.user_data['user_phone']
    selected_drink = context.user_data['selected_drink']

    data_storage.store_user_data(user_name, user_phone, selected_drink, recipe)

    # پایان مکالمه
    return ConversationHandler.END

# لغو مکالمه
def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('مکالمه لغو شد. اگر خواستی دوباره شروع کنی، /start رو بزن.')
    return ConversationHandler.END

def main() -> None:
    updater = Updater(token=config.TOKEN)
    dispatcher = updater.dispatcher

    # ساخت ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASK_PHONE: [MessageHandler(Filters.text & ~Filters.command, ask_drink)],
            ASK_DRINK: [MessageHandler(Filters.text & ~Filters.command, generate_and_send_recipe)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
