import csv
import os

# فایل CSV که داده‌ها در آن ذخیره می‌شود
FILE_PATH = 'user_data.csv'

def initialize_data_storage():
    """بررسی و ایجاد فایل CSV اگر وجود نداشته باشد."""
    if not os.path.exists(FILE_PATH):
        with open(FILE_PATH, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['نام کاربر', 'شماره تلفن', 'نوشیدنی انتخابی', 'رسپی'])

def store_user_data(user_name: str, user_phone: str, selected_drink: str, recipe: dict):
    """ذخیره اطلاعات کاربر و نوشیدنی انتخابی در فایل CSV."""
    recipe_text = "\n".join([f"{ingredient}: {quantity}" for ingredient, quantity in recipe.items()])
    new_data = [user_name, user_phone, selected_drink, recipe_text]

    with open(FILE_PATH, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(new_data)

def get_all_user_data():
    """خواندن تمام داده‌های ذخیره‌شده از فایل CSV."""
    data = []
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
    return data
