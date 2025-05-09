import random

# اینجا میتوانید لیست‌هایی از پاسخ‌ها برای سوالات مختلف اضافه کنید
responses = {
    'intro': [
        "سلام! به ربات Inotexdrinkbot خوش آمدید.\n"
        "برای شروع، چند سوال از شما می‌پرسیم تا نوشیدنی مناسب شما را پیشنهاد دهیم.",
        "سلام! خوش آمدید به ربات انتخاب نوشیدنی سرد.\n"
        "لطفاً با پاسخ دادن به چند سوال، به ما کمک کنید تا بهترین نوشیدنی را برای شما بسازیم."
    ],
    'sensitivity_question': [
        "آیا حساسیت غذایی خاصی دارید؟ (مثل شیر، گندم، گلوتن، ...) یا گزینه 'ندارم' را وارد کنید.",
        "لطفاً به ما بگویید آیا حساسیت غذایی دارید؟ یا اگر نه، لطفاً بنویسید 'ندارم'."
    ],
    'preference_question': [
        "آیا شما علاقه دارید نوشیدنی‌هایی با طعم میوه یا گیاهی داشته باشید؟",
        "دوست دارید نوشیدنی شما طعمی میوه‌ای داشته باشد یا گیاهی؟"
    ],
    'final_recipe': [
        "رسپی نوشیدنی شما آماده است: ",
        "نوشیدنی مورد نظر شما آماده است. در ادامه مواد لازم را مشاهده می‌کنید:"
    ],
    'error': [
        "متاسفانه مشکلی پیش آمده است. لطفاً دوباره تلاش کنید.",
        "پوزش می‌خواهیم، مشکلی رخ داده است. لطفاً دوباره امتحان کنید."
    ]
}

def get_response(key: str) -> str:
    """ تابعی برای دریافت پاسخ تصادفی از لیست پاسخ‌ها
    این تابع می‌تواند برای پاسخ‌های پیش‌فرض استفاده شود.
    """
    if key in responses:
        return random.choice(responses[key])
    else:
        return random.choice(responses['error'])

def generate_recipe_response(recipe: dict) -> str:
    """ تابع برای تولید پاسخ نهایی برای رسیپی نوشیدنی
    این تابع از اطلاعات رسیپی برای ساخت متن نهایی استفاده می‌کند.
    """
    recipe_text = "\n".join([f"{ingredient}: {quantity}" for ingredient, quantity in recipe.items()])
    return f"{get_response('final_recipe')}\n{recipe_text}"

def send_error_message() -> str:
    """ تابع برای ارسال پیام خطا """
    return get_response('error')

