import nest_asyncio
import asyncio
import random
import os
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
import google.generativeai as genai

# تنظیمات
nest_asyncio.apply()
TELEGRAM_TOKEN = '7756017839:AAGDutU2oiRDBVpE7U78kL9b8e7ViInBiUI'
OPENAI_API_KEY = 'AIzaSyC8VK_y5ESVLZNXI80wy7KBJ5_IxEoxh7E'
FILE_PATH = 'user_data.json'

# تنظیمات مدل
genai.configure(api_key=OPENAI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# مواد اولیه
ingredients = {
    'آب سیب': 50,
    'آب انار': 50,
    'آب آلبالو': 50,
    'آب پرتقال': 50,
    'آب آناناس': 50,
    'آب انگور سفید': 50,
    'آب انگور سیاه': 50,
    'نکتار انبه': 50,
    'نکتار پرتقال پالپ دار': 50,
    'نکتار هلو': 50,
    'نکتار هفت میوه': 50,
    'سیروپ توت فرنگی': 15,
    'سیروپ پشن فروت': 15,
    'سیروپ بلوبری': 15,
    'سیروپ بلک بری': 15,
    'سیروپ انگور': 15,
    'سیروپ گواوا': 15,
    'سیروپ موز': 15,
    'سیروپ بلوکارسائو': 15,
    'سیروپ گرین میکس': 15,
    'سیروپ گرانادین': 15,
    'سیروپ خیار': 15,
    'سیروپ هل': 5,
    'سیروپ فلفل': 5,
    'سیروپ بادیان': 5,
    'سیروپ ماسالا': 5,
    'ریحان': 5,
    'لیمو زرد': 10,
    'گل خوراکی': 5,
    'رزماری': 5,
    'نعنا تازه': 5,
    'توت فرنگی': 10,
    'پرتقال': 10
}

# ذخیره سازی اطلاعات
def initialize_data_storage():
    if not os.path.exists(FILE_PATH):
        with open(FILE_PATH, 'w') as f:
            json.dump([], f)

def store_user_data(user_name: str, user_phone: str, selected_drink: str, recipe: dict):
    new_data = {
        'نام کاربر': user_name,
        'شماره تلفن': user_phone,
        'نوشیدنی انتخابی': selected_drink,
        'رسپی': recipe
    }
    with open(FILE_PATH, 'r') as f:
        data = json.load(f)
    data.append(new_data)
    with open(FILE_PATH, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# تولید متن توسط مدل
def generate_text(prompt: str) -> str:
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"خطا در ارتباط با Gemini: {e}")
        return "خطایی رخ داده است."

# تولید رسپی، طرز تهیه، و خواص مواد
def generate_recipe(diet: str = 'normal', taste: str = 'sweet'):
    possible_ingredients = list(ingredients.keys())
    filtered_ingredients = random.sample(possible_ingredients, random.randint(4, 6))
    recipe = {item: f"{ingredients[item]} میلی لیتر" for item in filtered_ingredients}
    
    prompt_instructions = f"با استفاده از این مواد {', '.join(filtered_ingredients)} لطفاً یک طرز تهیه دقیق و حرفه‌ای نوشیدنی بنویس."
    prompt_benefits = f"خواص سلامتی و فواید مصرف این مواد را توضیح بده: {', '.join(filtered_ingredients)}"
    
    instructions = generate_text(prompt_instructions)
    benefits = generate_text(prompt_benefits)
    
    return recipe, instructions, benefits

# مراحل گفتگو
ASK_PHONE, ASK_DIET, ASK_TASTE = range(3)

async def start(update: Update, context) -> int:
    user = update.effective_user
    await update.message.reply_text(
        f"سلام {user.first_name} عزیز! 🌟\n"
        f"به ربات نوشیدنی‌ساز خوش آمدی!\n"
        f"من اینجا هستم تا یک نوشیدنی مخصوص و متناسب با سلیقه و رژیم غذایی‌ات برات بسازم. 🍹\n\n"
        f"ابتدا شماره تلفنت رو لطفاً وارد کن:"
    )
    return ASK_PHONE

async def ask_diet(update: Update, context) -> int:
    user_phone = update.message.text
    context.user_data['user_phone'] = user_phone
    await update.message.reply_text("آیا رژیم غذایی خاصی داری؟ (مثل کتوژنیک، وگان، معمولی و...)")
    return ASK_DIET

async def ask_taste(update: Update, context) -> int:
    user_diet = update.message.text
    context.user_data['user_diet'] = user_diet
    await update.message.reply_text("طعم مورد علاقه‌ات رو بگو: (شیرین، ترش، تلخ و...)")
    return ASK_TASTE

async def generate_and_send_recipe(update: Update, context) -> int:
    selected_taste = update.message.text
    context.user_data['selected_taste'] = selected_taste

    thinking_message = await update.message.reply_text('در حال فکر کردن هستم... 🤔')

    recipe, instructions, benefits = generate_recipe(
        diet=context.user_data['user_diet'],
        taste=context.user_data['selected_taste']
    )

    await thinking_message.delete()

    recipe_text = "\n".join([f"▫️ {ingredient}: {quantity}" for ingredient, quantity in recipe.items()])
    await update.message.reply_text(
        f"✨ نوشیدنی پیشنهادی شما:\n\n"
        f"{recipe_text}\n\n"
        f"📋 طرز تهیه:\n{instructions}\n\n"
        f"🌿 خواص مواد مصرفی:\n{benefits}"
    )

    store_user_data(update.effective_user.first_name, context.user_data['user_phone'], selected_taste, recipe)

    return ConversationHandler.END

async def cancel(update: Update, context) -> int:
    await update.message.reply_text("گفتگو لغو شد. امیدوارم دوباره ببینمت! 👋")
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
