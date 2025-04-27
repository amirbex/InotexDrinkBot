import os
import json

FILE_PATH = 'user_data.json'

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

def get_all_user_data():
    with open(FILE_PATH, 'r') as f:
        return json.load(f)
