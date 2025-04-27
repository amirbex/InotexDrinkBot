import pandas as pd
import os

# فایل اکسل که داده‌ها در آن ذخیره می‌شود
FILE_PATH = 'user_data.xlsx'

def initialize_data_storage():
    """ این تابع برای بررسی و ایجاد فایل اکسل استفاده می‌شود
    اگر فایل اکسل وجود نداشته باشد، آن را ایجاد می‌کند.
    """
    if not os.path.exists(FILE_PATH):
        # اگر فایل وجود نداشته باشد، یک فایل جدید با سرصفحه ایجاد می‌کنیم
        df = pd.DataFrame(columns=['نام کاربر', 'شماره تلفن', 'نوشیدنی انتخابی', 'رسپی'])
        df.to_excel(FILE_PATH, index=False)

def store_user_data(user_name: str, user_phone: str, selected_drink: str, recipe: dict):
    """ این تابع برای ذخیره‌سازی اطلاعات کاربر و نوشیدنی انتخابی او در فایل اکسل استفاده می‌شود.
    """
    # ابتدا داده‌ها را به یک DataFrame تبدیل می‌کنیم
    recipe_text = "\n".join([f"{ingredient}: {quantity}" for ingredient, quantity in recipe.items()])
    new_data = {
        'نام کاربر': user_name,
        'شماره تلفن': user_phone,
        'نوشیدنی انتخابی': selected_drink,
        'رسپی': recipe_text
    }

    # داده جدید را به فایل اکسل اضافه می‌کنیم
    df = pd.read_excel(FILE_PATH)
    df = df.append(new_data, ignore_index=True)
    df.to_excel(FILE_PATH, index=False)

def get_all_user_data():
    """ این تابع برای خواندن تمام داده‌های ذخیره‌شده از فایل اکسل استفاده می‌شود.
    """
    df = pd.read_excel(FILE_PATH)
    return df

