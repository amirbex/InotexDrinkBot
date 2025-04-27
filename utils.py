# utils.py

import random
import openpyxl
from drinks_data import ALL_INGREDIENTS

def generate_recipe():
    selected_ingredients = random.sample(ALL_INGREDIENTS, 4)
    quantities = [random.choice([30, 45, 60]) for _ in range(4)]

    steps = [
        "ابتدا لیوان را سرد کنید.",
        "سپس مواد انتخاب شده را به ترتیب داخل لیوان بریزید و خوب هم بزنید.",
        "در پایان سودا یا آب گازدار اضافه کنید."
    ]

    recipe = "\n".join([
        f"{ingredient}: {quantity} میلی لیتر"
        for ingredient, quantity in zip(selected_ingredients, quantities)
    ])

    final_text = f"مواد لازم:\n{recipe}\n\nمراحل تهیه:\n" + "\n".join(steps) + "\n\nویژگی نوشیدنی: تازه کننده و انرژی بخش 🍹"

    return final_text

def save_user_data(name, user_id, final_drink):
    try:
        workbook = openpyxl.load_workbook("database/users_data.xlsx")
        sheet = workbook.active
    except FileNotFoundError:
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(["نام", "آیدی تلگرام", "نوشیدنی انتخابی"])

    sheet.append([name, user_id, final_drink])
    workbook.save("database/users_data.xlsx")
