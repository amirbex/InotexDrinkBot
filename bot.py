from telegram import Update, CallbackContext

# استیج‌های گفتگو
ASK_PHONE, ASK_DIET, ASK_TASTE = range(3)

# استارت ربات
async def start(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    await update.message.reply_text(
        f"سلام {user.first_name} عزیز! خوش اومدی به Inotex Drink Bot 🍹\n"
        "لطفاً شماره تلفنت رو وارد کن:"
    )
    return ASK_PHONE

# دریافت شماره تلفن
async def ask_diet(update: Update, context: CallbackContext) -> int:
    user_phone = update.message.text
    context.user_data['user_phone'] = user_phone

    await update.message.reply_text(
        "حالا رژیم غذایی خود را وارد کن (مثلاً گیاه‌خواری، وگان و ...):"
    )
    return ASK_DIET

# دریافت رژیم غذایی
async def ask_taste(update: Update, context: CallbackContext) -> int:
    user_diet = update.message.text
    context.user_data['user_diet'] = user_diet

    await update.message.reply_text(
        "حالا لطفاً نوع طعم مورد علاقه‌ات رو وارد کن (مثلاً شیرین، ترش، تلخ و ...):"
    )
    return ASK_TASTE

# دریافت طعم و تولید رسپی
async def generate_and_send_recipe(update: Update, context: CallbackContext) -> int:
    selected_taste = update.message.text
    context.user_data['selected_taste'] = selected_taste

    # ارسال پیام "در حال فکر کردن هستم"
    thinking_message = await update.message.reply_text('در حال فکر کردن هستم...')

    # تولید رسپی
    recipe = recipe_generator.generate_recipe(
        diet=context.user_data['user_diet'],
        taste=context.user_data['selected_taste']
    )

    # حذف پیام "در حال فکر کردن هستم"
    await thinking_message.delete()

    # ساخت و ارسال رسپی
    recipe_text = "\n".join([f"{ingredient}: {quantity}" for ingredient, quantity in recipe.items()])
    await update.message.reply_text(
        f"این نوشیدنی پیشنهادی شماست:\n\n{recipe_text}"
    )

    # ذخیره اطلاعات در فایل
    user_name = update.effective_user.first_name
    user_phone = context.user_data['user_phone']
    selected_drink = context.user_data.get('selected_drink', 'نامشخص')

    data_storage.store_user_data(user_name, user_phone, selected_drink, recipe)

    return ConversationHandler.END
