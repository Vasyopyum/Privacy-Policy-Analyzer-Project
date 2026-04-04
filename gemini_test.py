import google.generativeai as genai

# Вставьте сюда свой ключ
genai.configure(api_key="AIzaSyAjs7r4yuJNCDA6UdLl1L9hCdTOaaBVdiA")

print("Список доступных моделей:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)