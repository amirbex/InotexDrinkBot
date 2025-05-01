import nest_asyncio
import asyncio
import random
import os
import json
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
import google.generativeai as genai

# --- تنظیمات اولیه ---
nest_asyncio.apply()
TELEGRAM_TOKEN = '7843819663:AAED6HyqaLKdANVHq3kvqvYua9koAJp14Ts'
GOOGLE_API_KEY = 'AIzaSyC8VK_y5ESVLZNXI80wy7KBJ5_IxEoxh7E'
FILE_PATH = 'user_data.json'

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")

# --- لیست مواد اولیه ---
ingredients = {
    # سیروپ
    'سیروپ پاپ کرن': 15, 'سیروپ بلک بری': 15, 'سیروپ گرانادین(انار با پوست)': 15, 'سیروپ زعفران': 15,
    'سیروپ خیار': 15, 'سیروپ گرین میکس': 15, 'سیروپ وانیل': 15, 'سیروپ شکلات': 15, 'سیروپ آیریش': 15,
    'سیروپ ردمیکس': 15, 'سیروپ پشن فروت': 15, 'سیروپ رام': 15, 'سیروپ آدامس آبی': 15,
    'سیروپ گواوا': 15, 'سیروپ ویمتو': 15, 'سیروپ کوکی': 15, 'سیروپ فندق': 15, 'سیروپ بادیان': 5,
    # آبمیوه
    'آب آلبالو': 50, 'آب پرتقال': 50, 'آب آناناس': 50, 'آب انار فلفلی': 50, 'آب سیب سبز': 50,
    'آب هلو': 50, 'آب انبه': 50, 'آب انگور سفید': 50, 'آب زردآلو': 50, 'آب انار': 50,
    # میوه و سبزیجات
    'ریحان ایتالیایی': 5, 'لیمو زرد': 10, 'گل خوراکی': 5, 'نعنا موهیتو تازه': 5,
    'توت فرنگی': 10, 'پرتقال تازه': 10,
    # عرقیات
    'عرق بیدمشک': 10, 'عرق بهارنارنج': 10,
    # گازدار
    'سودا کلاسیک': 80, 'سودا': 80, 'سیب گازدار': 80, 'انرژی زا': 80
}

# --- توابع ذخیره و بازیابی اطلاعات ---
def initialize_data_storage():
    if not os.path.exists(FILE_PATH):
        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False)

def store_user_data(user_id, key, value):
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if str(user_id) not in data:
        data[str(user_id)] = {}
    data[str(user_id)][key] = value
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

def get_user_data(user_id):
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get(str(user_id), {})

# --- تولید متن با جمینای ---
def generate_text(prompt: str):
    response = model.generate_content(prompt)
    return response.text.strip()

# --- تولید نوشیدنی ---
async def generate_drink(selected_diet: str, selected_taste: str):
    max_total_volume = 280
    max_syrup_volume = 40
    num_main_items = 6

    juices = {k: v for k, v in ingredients.items() if 'آب' in k}
    syrups = {k: v for k, v in ingredients.items() if 'سیروپ' in k}
    others = {k: v for k, v in ingredients.items() if k not in juices and k not in syrups}

    selected_items = []
    total_volume = 0
    syrup_volume = 0
    selected_names = set()

    pool = list(juices.items()) + list(syrups.items()) + list(others.items())
    random.shuffle(pool)

    attempts = 0
    while len(selected_items) < num_main_items and attempts < 100:
        for name, default_volume in pool:
            if name in selected_names:
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
            selected_names.add(name)
            total_volume += volume
            if is_syrup:
                syrup_volume += volume
            break
        attempts += 1

    # افزودن گازدار در انتها در صورت امکان
    if random.choice([True, False]) and total_volume < max_total_volume:
        soda_volume = max_total_volume - total_volume
        selected_items.append(('سودا', soda_volume))
        total_volume += soda_volume

    recipe = {name: f"{v} میلی‌لیتر" for name, v in selected_items}
    ingredients_list = "\n".join([f"- {name}: {v}ml" for name, v in selected_items])

    # --- ارتباط با جمینای ---
    prompt_main = (
        f"با توجه به طعم {selected_taste} و رژیم {selected_diet}، از مواد زیر یک نوشیدنی بدون الکل طراحی کن:\n"
        f"{ingredients_list}\n"
        f"لطفاً یک نام جذاب برای نوشیدنی پیشنهاد بده، سپس لیست مواد را مرتب و هماهنگ کن و در انتها یک جمله تبلیغاتی کوتاه هم بنویس."
    )
    prompt_instructions = f"طرز تهیه حرفه‌ای این نوشیدنی را به سبک یک بارتندر حرفه‌ای مرحله به مرحله بنویس:\n{ingredients_list}"
    prompt_benefits = f"خواص هر کدام از مواد زیر را برای سلامتی در یک پاراگراف مختصر بنویس:\n{ingredients_list}"

    text_main = generate_text(prompt_main)
    instructions = generate_text(prompt_instructions)
    benefits = generate_text(prompt_benefits)

    return recipe, text_main, instructions, benefits

# --- دستورات تلگرام ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply(f"سلام {user.first_name}! من یک ربات برای طراحی نوشیدنی‌های بدون الکل هستم. دستوراتی که می‌توانید استفاده کنید:\n"
                               "/create_drink - شروع ساخت نوشیدنی\n"
                               "/help - راهنمای استفاده")

async def create_drink(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    text = "لطفاً رژیم غذایی و طعم مورد نظر خود را انتخاب کنید."
    await update.message.reply(text)

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply("برای ساخت نوشیدنی، از دستور /create_drink استفاده کنید.")

# --- اجرا و مدیریت پیام‌ها ---
def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # دستورات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("create_drink", create_drink))

    # اجرای ربات
    application.run_polling()

if __name__ == '__main__':
    initialize_data_storage()
    main()
