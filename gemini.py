import os
import google.generativeai as genai

# مقداردهی اولیه به کلید API
genai.configure(api_key=OPENAI_API_KEY)


# انتخاب مدل
model = genai.GenerativeModel("gemini-pro")

def generate_text(prompt: str) -> str:
    """ ارسال پرامپت به Gemini و دریافت پاسخ """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"خطا در ارتباط با Gemini: {e}")
        return "خطایی رخ داده است."
