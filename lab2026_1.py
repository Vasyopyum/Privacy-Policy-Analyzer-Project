import gemini_test
from collections import Counter


def analyze_text(text: str) -> dict:
    # пустая стр
    if not text or not text.strip():
        return {"words_count": 0, "unique_words": 0, "longest_word": ""}
    words = re.findall(r'\b[а-яА-ЯёЁa-zA-Z0-9-]+\b', text)

    if not words:
        return {"words_count": 0, "unique_words": 0, "longest_word": ""}

    # смена регистра
    words_lower = [word.lower() for word in words]

    # уникальные слова
    unique_words_count = len(set(words_lower))

    #   длинное слово
    longest = max(words, key=len)

    return {
        "words_count": len(words),
        "unique_words": unique_words_count,
        "longest_word": longest
    }


# Обычный текст
result = analyze_text("Привет, мир! Привет, чудесный мир программирования.")
print(result)

# Пустая строка
result = analyze_text("")
print(result)

# Текст с разным регистром
result = analyze_text("Кот кошка КОТ КОШКА кот")
print(result)