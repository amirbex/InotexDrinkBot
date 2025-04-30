import nest_asyncio
import asyncio
import random
import os
import json
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
import google.generativeai as genai

# --- تنظیمات اولیه ---
nest_asyncio.apply()
TELEGRAM_TOKEN = '7843819663:AAED6HyqaLKdANVHq3kvqvYua9koAJp14Ts'
GOOGLE_API_KEY = 'AIzaSyC8VK_y5ESVLZNXI80wy7KBJ5_IxEoxh7E'
FILE_PATH = 'user_data.json'

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")

ingredients = {
    'آب سیب': 50, 'آب انار': 50, 'آب آلبالو': 50, 'آب پرتقال': 50, 'آب آناناس': 50,
    'آب انگور سفید': 50, 'آب انگور سیاه': 50, 'نکتار انبه': 50, 'نکتار پرتقال پالپ دار': 50,
    'نکتار هلو': 50, 'نکتار هفت میوه': 50, 'سیروپ توت فرنگی': 15, 'سیروپ پشن فروت': 15,
    'سیروپ بلوبری': 15, 'سیروپ بلک بری': 15, 'سیروپ انگور': 15, 'سیروپ گواوا': 15,
    'سیروپ موز': 15, 'سیروپ بلوکارسائو': 15, 'سیروپ گرین میکس': 15, 'سیروپ گرانادین': 15,
    'سیروپ خیار': 15, 'سیروپ هل': 5, 'سیروپ فلفل': 5, 'سیروپ بادیان': 5, 'سیروپ ماسالا': 5,
    'ریحان': 5, 'لیمو زرد': 10, 'گل خوراکی': 5, 'رزماری': 5, 'نعنا تازه': 5,
    'توت فرنگی': 10, 'پرتقال': 10
}

def initialize_data_storage():
    if not os.path.exists(FILE_PATH):
        with open(FILE_PATH, 'w') as f:
            json.dump([], f)

def store_user_data(user_name, user_phone, selected_drink, recipe):
    new_data = {
        'نام کاربر': user_name,
        'شماره تلفن': user_phone,
        'نوشیدنی انتخابی': selected_drink,
        'رسپی': recipe
    }
    if not os.path.exists(FILE_PATH) or os.stat(FILE_PATH).st_size == 0:
        data = []
    else:
        try:
            with open(FILE_PATH, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []

    data.append(new_data)

    with open(FILE_PATH, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def generate_text(prompt: str) -> str:
    try:
        response = model.generate_content([prompt])
        return response.candidates[0].content.parts[0].text
    except Exception as e:
        print(f"خطا در ارتباط با Gemini: {e}")
        return "خطایی در تولید متن رخ داده است."

async def generate_drink(selected_diet: str, selected_taste: str):
    max_total_volume = 280
    max_syrup_volume = 40
    num_main_items = 6

    juices = {k: v for k, v in ingredients.items() if 'آب' in k or 'نکتار' in k}
    syrups = {k: v for k, v in ingredients.items() if 'سیروپ' in k}
    others = {k: v for k, v in ingredients.items() if k not in juices and k not in syrups}

    selected_items = []
    total_volume = 0
    syrup_volume = 0

    while len(selected_items) < num_main_items:
        pool = list(juices.items()) + list(syrups.items()) + list(others.items())
        random.shuffle(pool)
        for name, default_volume in pool:
            if name in dict(selected_items):
                continue

            is_syrup = 'سیروپ' in name
            if name in juices:
                volume = random.choice([20, 30, 40, 50, 60, 80])
            elif is_syrup:
                volume = random.choice([10, 20, 30, 40])
            else:
                volume = default_volume

            if is_syrup and syrup_volume + volume > max_syrup_volume:
                continue
            if total_volume + volume > max_total_volume:
                continue

            selected_items.append((name, volume))
            total_volume += volume
            if is_syrup:
                syrup_volume += volume
            break

    # گاهی "سودا" را به عنوان آیتم هفتم اضافه می‌کنیم
    add_soda = random.choice([True, False])
    if add_soda and total_volume < max_total_volume:
        soda_volume = max_total_volume - total_volume
        selected_items.append(('سودا', soda_volume))
        total_volume += soda_volume

    recipe = {name: f"{v} میلی‌لیتر" for name, v in selected_items}
    ingredients_list = "\n".join([f"- {name}: {v}ml" for name, v in selected_items])

    instruction_prompt = (
        f"یک دستور تهیه دقیق برای نوشیدنی بدون الکل با مواد زیر بنویس:\n{ingredients_list}\n"
        f"طعم باید {selected_taste} باشد و مناسب رژیم {selected_diet}. لطفاً مرحله به مرحله توضیح بده."
    )

    benefits_prompt = (
        f"خواص سلامتی هر یک از این مواد را به طور مختصر بنویس:\n{ingredients_list}"
    )

    instructions = generate_text(instruction_prompt)
    benefits = generate_text(benefits_prompt)

    return recipe, instructions, benefits


# --- وضعیت‌های مکالمه ---
ASK_PHONE, ASK_DIET, ASK_TASTE, AFTER_RECIPE = range(4)

async def start(update: Update, context):
    user = update.effective_user
    await update.message.reply_text(
        f"سلام {user.first_name}! 👋✨\n\n"
        "من دستیار هوشمند تهیه دستورالعمل نوشیدنی در غرفه‌ی اکسیر در نمایشگاه اینوتکس 2025 هستم با چند تا سوال خیلی سریع بهت یه دستورالعمل میدم . 🍹🎉\n"
        "خوشحالم که اینجایی! برای شروع لطفاً شماره موبایلت رو وارد کن 📱"
    )
    return ASK_PHONE

async def ask_diet(update: Update, context):
    context.user_data['user_phone'] = update.message.text
    await update.message.reply_text(
        "ممنونم! 🌟\n"
        "حالا میشه بگی رژیم غذایی خاصی داری؟ مثلاً:\n"
        "معمولی، وگان، بدون قند، کم کالری یا هر چیزی که دوست داری... 🍃"
    )
    return ASK_DIET

async def ask_taste(update: Update, context):
    context.user_data['user_diet'] = update.message.text
    await update.message.reply_text(
        "عالیه! 😍\n"
        "حالا بگو طعم دلخواهت چیه؟\n"
        "شیرین، ترش، متعادل یا هر چیزی که دوست داری بنوشی 🍯🍋✨"
    )
    return ASK_TASTE

async def generate_and_send_recipe(update: Update, context):
    context.user_data['selected_taste'] = update.message.text
    thinking_message = await update.message.reply_text('🤔 دارم بهترین نوشیدنی رو برات آماده می‌کنم... لطفاً چند لحظه صبر کن! 🍸')

    recipe, instructions, benefits = await generate_drink(
        selected_diet=context.user_data['user_diet'],
        selected_taste=context.user_data['selected_taste']
    )

    await thinking_message.delete()

    recipe_text = "\n".join([f"▫️ {ingredient}: {amount}" for ingredient, amount in recipe.items()])
    await update.message.reply_text(f"📋 مواد اولیه نوشیدنی شما:\n\n{recipe_text}")

    instructions_text = "\n".join([f"▫️ {ingredient}" for ingredient in recipe.keys()]) + f"\n\n{instructions}"
    await update.message.reply_text(f"🍸 طرز تهیه:\n\n{instructions_text}")

    benefits_text = "\n".join([f"▫️ {ingredient}" for ingredient in recipe.keys()]) + f"\n\n{benefits}"
    await update.message.reply_text(f"🌿 خواص سلامتی:\n\n{benefits_text}")

    store_user_data(
        update.effective_user.first_name,
        context.user_data['user_phone'],
        context.user_data['selected_taste'],
        recipe
    )

    reply_keyboard = [['🔁 تغییر رسپی', 'ℹ️ اطلاعات بیشتر'], ['❌ پایان']]
    await update.message.reply_text(
        "آیا دوست داری کاری دیگه انجام بدی؟",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )

    return AFTER_RECIPE

async def after_recipe(update: Update, context):
    text = update.message.text
    if 'تغییر' in text:
        return await generate_and_send_recipe(update, context)
    elif 'اطلاعات بیشتر' in text:
        await update.message.reply_text("چه اطلاعاتی دوست داری بدونی؟ مثلاً درباره‌ی هر ماده خاص؟ (این بخش می‌تونه توسعه پیدا کنه)")
        return AFTER_RECIPE
    else:
        await update.message.reply_text("با آرزوی سلامتی 🍹 تا بعد!")
        return ConversationHandler.END

async def cancel(update: Update, context):
    await update.message.reply_text("❌ گفتگو لغو شد. هر زمان خواستی با /start دوباره شروع کن.")
    return ConversationHandler.END

async def main():
    initialize_data_storage()
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_diet)],
            ASK_DIET: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_taste)],
            ASK_TASTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, generate_and_send_recipe)],
            AFTER_RECIPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, after_recipe)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    application.add_handler(conv_handler)
    await application.run_polling()

if
