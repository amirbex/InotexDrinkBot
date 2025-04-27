import random

# لیست مواد اولیه
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

# برچسب زدن ساده برای رژیم و طعم
diet_ingredients = {
    'vegan': ['آب سیب', 'آب انار', 'آب پرتقال', 'آب آلبالو', 'آب آناناس', 'آب انگور سفید', 'آب انگور سیاه', 'نکتار انبه', 'نکتار هلو'],
    'normal': list(ingredients.keys()),  # همه چیز مجاز
}

taste_ingredients = {
    'sweet': ['آب سیب', 'نکتار انبه', 'سیروپ توت فرنگی', 'سیروپ بلوبری', 'سیروپ موز'],
    'sour': ['آب انار', 'آب آلبالو', 'لیمو زرد', 'سیروپ پشن فروت'],
    'bitter': ['سیروپ هل', 'سیروپ ماسالا', 'رزماری']
}

def generate_recipe(diet: str = 'normal', taste: str = 'sweet') -> dict:
    """ تولید رسیپی با درنظر گرفتن رژیم و طعم """
    
    possible_ingredients = set(diet_ingredients.get(diet, ingredients.keys()))
    taste_based_ingredients = set(taste_ingredients.get(taste, ingredients.keys()))
    
    filtered_ingredients = list(possible_ingredients & taste_based_ingredients)
    
    # اگر تقاطعی وجود نداشت، بیخیال taste می‌شود
    if not filtered_ingredients:
        filtered_ingredients = list(possible_ingredients)

    num_ingredients = random.randint(4, 6)
    selected = random.sample(filtered_ingredients, min(num_ingredients, len(filtered_ingredients)))

    recipe = {}
    for item in selected:
        quantity = ingredients[item]
        recipe[item] = f"{quantity} میلی لیتر"

    recipe['دستورالعمل'] = "لیوان را سرد کرده و مواد انتخاب شده را با یخ مخلوط کنید. سرو کنید."

    return recipe
