import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
from openai import OpenAI


# --- 1. ФУНКЦИИ (МЕХАНИЗМЫ) ---

def get_policy_text(url):
    """Вытягивает текст из веб-страницы"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}  # Чтобы сайты не блокировали "бота"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Удаляем лишние элементы (скрипты, стили, навигацию)
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()

        text = soup.get_text(separator=' ')
        # Чистим от лишних пробелов и берем первые 12000 символов
        clean_text = " ".join(text.split())
        return clean_text[:12000]
    except Exception as e:
        return f"Ошибка загрузки текста: {e}"


def analyze_policy_with_ai(policy_text, api_key):
    """Отправляет текст в OpenAI и получает JSON-анализ"""
    client = OpenAI(api_key=api_key)

    system_instruction = """
    Ты — эксперт по защите персональных данных. Проанализируй текст политики конфиденциальности.
    Верни ответ СТРОГО в формате JSON на русском языке.
    Структура JSON:
    {
      "risk_level": "Low" | "Medium" | "High",
      "summary": "Краткое описание на 2 предложения",
      "red_flags": [
        {"point": "в чем риск", "quote": "цитата из текста"}
      ]
    }
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Быстрая и дешевая модель
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"Проанализируй этот текст: {policy_text}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": f"Ошибка ИИ: {str(e)}"}


# --- 2. ИНТЕРФЕЙС (STREAMLIT) ---

st.set_page_config(page_title="Privacy Analyzer", page_icon="🕵️‍♂️")

st.title("🕵️‍♂️ Анализатор политик конфиденциальности")
st.write("Вставьте ссылку на политику, чтобы ИИ нашел скрытые угрозы.")

# Боковая панель для настроек
with st.sidebar:
    st.header("Настройки")
    api_key = st.text_input("OpenAI API Key:", type="password")
    st.info("Ключ можно получить в личном кабинете OpenAI.")

# Основное поле ввода
url = st.text_input("URL политики конфиденциальности:", placeholder="https://example.com/privacy")

if st.button("Начать анализ", type="primary"):
    if not api_key:
        st.error("Пожалуйста, введите API Key в боковой панели.")
    elif not url:
        st.warning("Введите адрес сайта.")
    else:
        # ШАГ 1: Парсинг
        with st.status("Сканирую страницу...") as status:
            policy_content = get_policy_text(url)
            if "Ошибка" in policy_content:
                st.error(policy_content)
            else:
                status.update(label="Текст получен! Анализирую через ИИ...", state="running")

                # ШАГ 2: Анализ ИИ
                result = analyze_policy_with_ai(policy_content, api_key)

                if "error" in result:
                    st.error(result["error"])
                else:
                    status.update(label="Анализ завершен!", state="complete")

                    # ШАГ 3: Вывод результата
                    st.divider()

                    # Цветовая индикация риска
                    risk = result.get("risk_level", "Low")
                    if risk == "High":
                        st.error(f"### Уровень риска: {risk}")
                    elif risk == "Medium":
                        st.warning(f"### Уровень риска: {risk}")
                    else:
                        st.success(f"### Уровень риска: {risk}")

                    st.write(f"**Резюме:** {result.get('summary')}")

                    st.subheader("🚩 Красные флаги:")
                    for flag in result.get("red_flags", []):
                        with st.expander(f"⚠️ {flag['point']}"):
                            st.write(f"*Цитата из текста:*")
                            st.caption(f"«{flag['quote']}»")