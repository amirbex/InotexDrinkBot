import nest_asyncio
import asyncio
import random
import os
import json
from telegram import Update
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

# --- توابع ---
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
    # اگر فایل خالی یا خراب بود، data رو [] در نظر بگیر
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
    possible_ingredients = list(ingredients.keys())
    selected_items = random.sample(possible_ingredients, random.randint(4, 6))
    recipe = {item: f"{ingredients[item]} میلی لیتر" for item in selected_items}

    # آماده‌سازی دیتای دقیق برای مدل
    ingredients_list = "\n".join([f"- {item}: {ingredients[item]}ml" for item in selected_items])

    instruction_prompt = (
        f"یک دستور تهیه دقیق و حرفه‌ای برای یک نوشیدنی بدون الکل فقط با مواد زیر بنویس. "
        f"طعم نوشیدنی باید {selected_taste} باشد و مناسب رژیم {selected_diet} طراحی شود:\n{ingredients_list}\n"
        "لطفاً مرحله به مرحله توضیح بده."
    )

    benefits_prompt = (
        f"خواص و فواید سلامتی هر یک از این مواد را جداگانه و مختصر توضیح بده:\n{ingredients_list}"
    )

    instructions = generate_text(instruction_prompt)
    benefits = generate_text(benefits_prompt)

    return recipe, instructions, benefits

# --- وضعیت‌های مکالمه ---
ASK_PHONE, ASK_DIET, ASK_TASTE = range(3)

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

    # نمایش مواد اولیه با مقدار
    recipe_text = "\n".join([f"▫️ {ingredient}: {amount}" for ingredient, amount in recipe.items()])
    await update.message.reply_text(f"📋 مواد اولیه نوشیدنی شما:\n\n{recipe_text}")

    # نمایش طرز تهیه فقط با نام مواد بدون مقدار
    instructions_text = "\n".join([f"▫️ {ingredient}" for ingredient in recipe.keys()]) + f"\n\n{instructions}"
    await update.message.reply_text(f"🍸 طرز تهیه:\n\n{instructions_text}")

    # نمایش خواص سلامتی فقط با نام مواد
    benefits_text = "\n".join([f"▫️ {ingredient}" for ingredient in recipe.keys()]) + f"\n\n{benefits}"
    await update.message.reply_text(f"🌿 خواص سلامتی:\n\n{benefits_text}")

    store_user_data(
        update.effective_user.first_name,
        context.user_data['user_phone'],
        context.user_data['selected_taste'],
        recipe
    )

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
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    application.add_handler(conv_handler)
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
